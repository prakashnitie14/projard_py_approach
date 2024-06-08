package com.corporate.riskmanagement.services;

import com.corporate.riskmanagement.domain.CompanyFinancialAnalysis;
import com.corporate.riskmanagement.langchain.constructs.FinancialDataExtractor;
import lombok.AllArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.ai.chat.messages.UserMessage;
import org.springframework.ai.chat.prompt.Prompt;
import org.springframework.ai.chat.prompt.PromptTemplate;
import org.springframework.ai.chat.prompt.SystemPromptTemplate;
import org.springframework.ai.document.Document;
import org.springframework.ai.document.DocumentReader;
import org.springframework.ai.huggingface.HuggingfaceChatClient;
import org.springframework.ai.parser.BeanOutputParser;
import org.springframework.ai.reader.tika.TikaDocumentReader;
import org.springframework.ai.transformers.TransformersEmbeddingClient;
import org.springframework.ai.vectorstore.SearchRequest;
import org.springframework.ai.vectorstore.VectorStore;
import org.springframework.core.io.InputStreamResource;
import org.springframework.stereotype.Service;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.multipart.MultipartFile;

import java.io.ByteArrayInputStream;
import java.io.IOException;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

@Service
@AllArgsConstructor
@Slf4j
public class AiService {
    private final HuggingfaceChatClient chatClient;
    private final TransformersEmbeddingClient embeddingClient;
    private final VectorStore vectorStore;
    private List<String> docIds;

    public String clearVectorStore() throws IOException {
        vectorStore.delete(docIds);
        return "true";
    }
    public Object chatWithModelUsingVectorStore(@RequestParam MultipartFile file) throws IOException {
        log.info("Persisting document with name={} in the vector store", file.getOriginalFilename());
        DocumentReader documentReader = new TikaDocumentReader(new InputStreamResource(new ByteArrayInputStream(file.getBytes())));
        List<Document> documents = documentReader.get();
        vectorStore.add(documents);
        docIds = documents.stream().map(Document::getId).toList();
        Object response1 = extractFinancialData("""
            Extract data in the below format from the provided financial documents
                {format}
            """, FinancialDataExtractor.PROMPT);
        return response1;
    }

    private Object extractFinancialData(String query, String systemPrompt) {
        log.info("Performing similarity search for query={}", query);
        List<Document> similarDocuments = vectorStore.similaritySearch(SearchRequest.query(query).withTopK(5));
        String documents = similarDocuments.stream().map(Document::getContent).collect(Collectors.joining(System.lineSeparator()));
        var systemPromptTemplate = new SystemPromptTemplate(systemPrompt);
        var systemMessageDocs = systemPromptTemplate.createMessage(
                Map.of("information", documents));

        var statementsByPeriodBeanOutputParser = new BeanOutputParser<>(CompanyFinancialAnalysis.FinancialData.class);

        PromptTemplate userMessagePromptTemplate = new PromptTemplate(query);
        userMessagePromptTemplate.setOutputParser(statementsByPeriodBeanOutputParser);
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
        Object financialData = response;
        try {
            financialData = statementsByPeriodBeanOutputParser.parse(response);
            log.info("Extracted entities {}", financialData);
        }
        catch(Exception e){
            log.warn("Unable to parse response {}", e.getMessage());
        }
        return financialData;
    }
}
