package com.corporate.riskmanagement.api;

import com.corporate.riskmanagement.domain.CompanyFinancialAnalysis;
import com.corporate.riskmanagement.langchain.constructs.FinancialDataExtractor;
import com.fasterxml.jackson.core.JsonProcessingException;
import dev.langchain4j.data.document.Document;
import dev.langchain4j.data.document.DocumentSplitter;
import dev.langchain4j.data.document.parser.apache.pdfbox.ApachePdfBoxDocumentParser;
import dev.langchain4j.data.document.splitter.DocumentSplitters;
import dev.langchain4j.data.embedding.Embedding;
import dev.langchain4j.data.segment.TextSegment;
import dev.langchain4j.memory.ChatMemory;
import dev.langchain4j.memory.chat.MessageWindowChatMemory;
import dev.langchain4j.model.chat.ChatLanguageModel;
import dev.langchain4j.model.embedding.EmbeddingModel;
import dev.langchain4j.rag.content.retriever.ContentRetriever;
import dev.langchain4j.rag.content.retriever.EmbeddingStoreContentRetriever;
import dev.langchain4j.service.AiServices;
import dev.langchain4j.store.embedding.EmbeddingStore;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import java.io.FileInputStream;
import java.io.FileNotFoundException;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.List;

@RestController
@Slf4j
public class LangchainDocumentAPI {
    private final EmbeddingModel embeddingModel;
    private final ChatLanguageModel chatLanguageModel;
    private final EmbeddingStore embeddingStore;

    @Autowired
    public LangchainDocumentAPI(EmbeddingModel embeddingModel, ChatLanguageModel chatLanguageModel, EmbeddingStore embeddingStore) {
        this.embeddingModel = embeddingModel;
        this.chatLanguageModel = chatLanguageModel;
        this.embeddingStore = embeddingStore;
    }

    @GetMapping("/v2/rag/document")
    public void chatWithModelUsingLangchain(@RequestParam String query) throws JsonProcessingException, FileNotFoundException {
        Path path = Paths.get("/Users/sahanapranesh/Downloads/Archive (1)/Whole Balance sheets - updated - v2 (v1 errors removed)/Company 1 - Full Balance Sheet - Sheet1-10.pdf");
        log.info("Processing request for query={}", query);
        ApachePdfBoxDocumentParser apachePdfBoxDocumentParser = new ApachePdfBoxDocumentParser();
        Document document = apachePdfBoxDocumentParser.parse(new FileInputStream(path.toFile()));
        DocumentSplitter splitter = DocumentSplitters.recursive(1000, 200);
        List<TextSegment> segments = splitter.split(document);
        List<Embedding> embeddings = embeddingModel.embedAll(segments).content();
        log.info("segments size={}", segments.size());
        log.info("Embeddings size={}", embeddings.size());

        embeddingStore.addAll(embeddings, segments);

        ChatMemory chatMemory = MessageWindowChatMemory.builder().maxMessages(10).build();
        ContentRetriever contentRetriever = EmbeddingStoreContentRetriever.builder()
                .embeddingStore(embeddingStore)
                .embeddingModel(embeddingModel)
                .minScore(0.4)
                .build();

        log.info("Extracting data from language model");
        FinancialDataExtractor extractor =
                AiServices.builder(FinancialDataExtractor.class)
                        .chatLanguageModel(chatLanguageModel)
                        .contentRetriever(contentRetriever)
                        .chatMemory(chatMemory)
                        .build();
        CompanyFinancialAnalysis.IncomeStatementRecords incomeStatement = extractor.getIncomeAnalysis("Analyse the combined statement of income table. Dont offer any explanation");
        log.info("Extracted income statement={}", incomeStatement);
        CompanyFinancialAnalysis.BalanceSheetRecords balanceSheet = extractor.getBalanceSheetAnalysis("segregate data from balance sheet as per current year and the previous year");
        log.info("Extracted balance sheet={}", balanceSheet);
    }

}
