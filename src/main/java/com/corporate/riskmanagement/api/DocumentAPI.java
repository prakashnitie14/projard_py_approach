package com.corporate.riskmanagement.api;

import com.corporate.riskmanagement.domain.CompanyFinancialAnalysis;
import com.fasterxml.jackson.core.JsonProcessingException;
import lombok.extern.slf4j.Slf4j;
import org.springframework.ai.chat.messages.UserMessage;
import org.springframework.ai.chat.prompt.Prompt;
import org.springframework.ai.chat.prompt.PromptTemplate;
import org.springframework.ai.chat.prompt.SystemPromptTemplate;
import org.springframework.ai.document.Document;
import org.springframework.ai.huggingface.HuggingfaceChatClient;
import org.springframework.ai.parser.BeanOutputParser;
import org.springframework.ai.vectorstore.SearchRequest;
import org.springframework.ai.vectorstore.VectorStore;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

@RestController
@Slf4j
public class DocumentAPI {
    private final HuggingfaceChatClient chatClient;
    private final VectorStore vectorStore;

    @Autowired
    DocumentAPI(HuggingfaceChatClient chatClient, VectorStore vectorStore) {
        this.chatClient = chatClient;
        this.vectorStore = vectorStore;
    }

    @GetMapping("/rag/document/")
    public void chatWithModelUsingVectorStore(@RequestParam String attribute,@RequestParam String year) throws JsonProcessingException {
        List<Document> similarDocuments = vectorStore.similaritySearch(SearchRequest.query(attribute).withTopK(2));
        String documents = similarDocuments.stream().map(Document::getContent).collect(Collectors.joining(System.lineSeparator()));
        String systemMessage = """
                <s>[INST] You are a helpful assistant.
                              
                Use the following information to answer the questionS in a structured JSON format:
                {information}
                [/INST]</s>
                [INST] Don't assume answers. Please provide only information that is present on the document [/INST]""";
        var systemPromptTemplate = new SystemPromptTemplate(systemMessage);
        var systemMessageDocs = systemPromptTemplate.createMessage(
                Map.of("information", documents));

        var outputParser = new BeanOutputParser<>(CompanyFinancialAnalysis.class);
        PromptTemplate userMessagePromptTemplate = new PromptTemplate("""
                                                                          You are a financial analysis API specializing in analysing balance sheets that responds in a valid JSON.
                                                                          Your job is to extract structured financial data from an unstructured bank note and output the structured data in JSON.
                                                                          You need to determine the years for which the financial data has been presented and segregate the data according to the years.\\s
                                                                          The JSON schema should include:
                                                                          1. The name of the company.
                                                                          2. If the income statement has been provided, extract the gross profit, cost of sales and income before taxes.
                                                                          3. If the balance sheet has been provided, extract the total current assets and total current liabilities. 
                                                                          4. Segregate the data according to the years that have been provided 
                                                                          5. If any data is missing, the value should be null. 
                """);
        Map<String,Object> model = Map.of("attribute", attribute,
                "year", year,
                "format", outputParser.getFormat());
        var userMessage = new UserMessage(userMessagePromptTemplate.create(model).getContents());

        var prompt = new Prompt(List.of(systemMessageDocs, userMessage));

        var response = chatClient.call(prompt).getResult().getOutput().getContent();

        System.out.println(response);
        System.out.println(outputParser.parse(response));
    }
}
