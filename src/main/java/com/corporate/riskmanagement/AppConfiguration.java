package com.corporate.riskmanagement;


import dev.langchain4j.model.huggingface.HuggingFaceChatModel;
import dev.langchain4j.model.huggingface.HuggingFaceEmbeddingModel;
import dev.langchain4j.store.embedding.EmbeddingStore;
import dev.langchain4j.store.embedding.inmemory.InMemoryEmbeddingStore;
import lombok.extern.slf4j.Slf4j;
import org.springframework.ai.document.DocumentReader;
import org.springframework.ai.embedding.EmbeddingClient;
import org.springframework.ai.huggingface.HuggingfaceChatClient;
import org.springframework.ai.reader.pdf.PagePdfDocumentReader;
import org.springframework.ai.vectorstore.SimpleVectorStore;
import org.springframework.ai.vectorstore.VectorStore;
import org.springframework.boot.ApplicationRunner;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.core.io.FileSystemResource;

import java.nio.file.Path;
import java.nio.file.Paths;

@Configuration
@Slf4j
public class AppConfiguration {
    private static final String HF_TOKEN="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";
    private static final String EMBEDDING_MODEL="sentence-transformers/all-mpnet-base-v2";
    private static final String LLM="mistralai/Mistral-7B-Instruct-v0.2";

    @Bean
    VectorStore vectorStore(EmbeddingClient embeddingClient) {
            return new SimpleVectorStore(embeddingClient);
    }

    @Bean
    EmbeddingStore embeddingStore() {
        return new InMemoryEmbeddingStore();
    }

    @Bean
    HuggingfaceChatClient chatClient() {
        return new HuggingfaceChatClient("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",
                "https://hcwqdczb7dx0ksck.us-east-1.aws.endpoints.huggingface.cloud");
    }

    @Bean
    HuggingFaceEmbeddingModel huggingFaceEmbeddingModel() {
        return new HuggingFaceEmbeddingModel.HuggingFaceEmbeddingModelBuilder()
                .modelId(EMBEDDING_MODEL)
                .accessToken(HF_TOKEN)
                .build();
    }

    @Bean
    HuggingFaceChatModel huggingFaceChatModel() {
        return new HuggingFaceChatModel.Builder()
                .accessToken(HF_TOKEN)
                .modelId(LLM)
                .build();
    }

    @Bean
    ApplicationRunner runner(VectorStore vectorStore) {
            Path path = Paths.get("/Users/sahanapranesh/Downloads/Company 2 - Sheet1.pdf");
            return args -> {
                log.info("Loading file(s) as Documents");
                DocumentReader documentReader = new PagePdfDocumentReader(new FileSystemResource(path));
                vectorStore.add(documentReader.get());
            };
    }

}
