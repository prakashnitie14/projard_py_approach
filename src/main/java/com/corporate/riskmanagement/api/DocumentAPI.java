package com.corporate.riskmanagement.api;

import com.corporate.riskmanagement.domain.CompanyFinancialAnalysis;
import lombok.extern.slf4j.Slf4j;
import org.springframework.ai.chat.messages.UserMessage;
import org.springframework.ai.chat.prompt.Prompt;
import org.springframework.ai.chat.prompt.PromptTemplate;
import org.springframework.ai.chat.prompt.SystemPromptTemplate;
import org.springframework.ai.document.Document;
import org.springframework.ai.document.DocumentReader;
import org.springframework.ai.embedding.EmbeddingClient;
import org.springframework.ai.huggingface.HuggingfaceChatClient;
import org.springframework.ai.parser.BeanOutputParser;
import org.springframework.ai.reader.pdf.PagePdfDocumentReader;
import org.springframework.ai.vectorstore.SearchRequest;
import org.springframework.ai.vectorstore.VectorStore;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.core.io.InputStreamResource;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.multipart.MultipartFile;

import java.io.ByteArrayInputStream;
import java.io.IOException;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

@RestController
@Slf4j
public class DocumentAPI {
    private final HuggingfaceChatClient chatClient;
    private final VectorStore vectorStore;
    String systemMessage = """
                <s>[INST] You are a financial analysis API specializing in analysing income statements.\n" +
                "Your job is to extract structured financial data from companys' financial statements and output the structured data.\n </s>" +
                "Give precise answers to what you are asked from the information provided to you.\n" +
                "You need to determine the years for which the financial data has been presented and segregate the data according to the years.
                {information}
                [/INST]</s>
                [INST] Don't assume answers. Please provide only information that is present on the document [/INST]""";

    @Autowired
    DocumentAPI(HuggingfaceChatClient chatClient, VectorStore vectorStore) {
        this.chatClient = chatClient;
        this.vectorStore = vectorStore;
    }

    @PostMapping("/rag/document/")
    public CompanyFinancialAnalysis.FinancialData chatWithModelUsingVectorStore(@RequestParam MultipartFile file) throws IOException {
        log.info("Persisting document with name={} in the vector store", file.getOriginalFilename());
        DocumentReader documentReader = new PagePdfDocumentReader(new InputStreamResource(new ByteArrayInputStream(file.getBytes())));

        vectorStore.add(documentReader.get());
        CompanyFinancialAnalysis.IncomeStatementRecords incomeStatementRecords = (CompanyFinancialAnalysis.IncomeStatementRecords) extractFinancialData("""
            [INST] Extract data in the below format from the income statement 
                {format}
            [/INST]
            """, CompanyFinancialAnalysis.IncomeStatementRecords.class);
        CompanyFinancialAnalysis.BalanceSheetRecords balanceSheetRecords = (CompanyFinancialAnalysis.BalanceSheetRecords) extractFinancialData("""
            [INST] Extract the below data from the balance sheet 
                {format}
            [/INST]
            """, CompanyFinancialAnalysis.BalanceSheetRecords.class);
        return CompanyFinancialAnalysis.FinancialData.builder().balanceSheet(balanceSheetRecords).incomeStatement(incomeStatementRecords).build();
    }

    private Object extractFinancialData(String query, Class outputParser) {
        log.info("Performing similarity search for query={}", query);
        List<Document> similarDocuments = vectorStore.similaritySearch(SearchRequest.query(query).withTopK(5));
        String documents = similarDocuments.stream().map(Document::getContent).collect(Collectors.joining(System.lineSeparator()));
        var systemPromptTemplate = new SystemPromptTemplate(systemMessage);
        var systemMessageDocs = systemPromptTemplate.createMessage(
                Map.of("information", documents));

        var statementsByPeriodBeanOutputParser = new BeanOutputParser<>(outputParser);

        PromptTemplate userMessagePromptTemplate = new PromptTemplate(query);
        Map<String,Object> model = Map.of(
                "format", statementsByPeriodBeanOutputParser.getFormat());
        var userMessage = new UserMessage(userMessagePromptTemplate.create(model).getContents());

        var prompt = new Prompt(List.of(systemMessageDocs, userMessage));
        log.info("Calling chat client with prompt={}", prompt);
        var response = chatClient.call(prompt).getResult().getOutput().getContent();

        log.info("RESPONSE Received={}", response);
        if(response.startsWith("```json")){
            response = response.substring(7,response.lastIndexOf("```"));
        }
        return statementsByPeriodBeanOutputParser.parse(response);
    }
}
