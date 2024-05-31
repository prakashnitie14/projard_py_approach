package com.corporate.riskmanagement;


import com.corporate.riskmanagement.langchain.constructs.HuggingFaceChatLanguageModel;
import com.corporate.riskmanagement.langchain.constructs.HuggingFaceClient;
import dev.langchain4j.store.embedding.EmbeddingStore;
import dev.langchain4j.store.embedding.inmemory.InMemoryEmbeddingStore;
import lombok.extern.slf4j.Slf4j;
import org.springframework.ai.document.MetadataMode;
import org.springframework.ai.embedding.EmbeddingClient;
import org.springframework.ai.huggingface.HuggingfaceChatClient;
import org.springframework.ai.transformers.TransformersEmbeddingClient;
import org.springframework.ai.vectorstore.SimpleVectorStore;
import org.springframework.ai.vectorstore.VectorStore;
import org.springframework.beans.factory.annotation.Qualifier;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.context.annotation.Primary;
import org.springframework.web.servlet.config.annotation.CorsRegistry;
import org.springframework.web.servlet.config.annotation.WebMvcConfigurer;

import java.time.Duration;

@Configuration
@Slf4j
public class AppConfiguration {
    private static final String HF_TOKEN="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";
    private static final String EMBEDDING_MODEL="sentence-transformers/all-mpnet-base-v2";
    private static final String EMBEDDING_ENDPOINT="https://s2yfs55xbdbjwc14.us-east-1.aws.endpoints.huggingface.cloud";
    private static final String LLM="mistralai/Mistral-7B-Instruct-v0.2";
    private static final String MiSTRAL_INFERENCE_ENDPOINT="https://hcwqdczb7dx0ksck.us-east-1.aws.endpoints.huggingface.cloud";
    private static final String LLAMA3_INFERENCE_ENDPOINT="https://j7xzywx6eone6oc3.us-east-1.aws.endpoints.huggingface.cloud";

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
        return new HuggingfaceChatClient(HF_TOKEN,
                MiSTRAL_INFERENCE_ENDPOINT);
    }

    @Bean
    TransformersEmbeddingClient embeddingClient(){
        return new TransformersEmbeddingClient(MetadataMode.NONE);
    }

    @Bean
    @Primary
    HuggingFaceClient huggingFaceClient(){
        return new HuggingFaceClient(HF_TOKEN, Duration.ofMinutes(5), MiSTRAL_INFERENCE_ENDPOINT);
    }

    @Bean
    @Qualifier("huggingFaceEmbeddingClient")
    HuggingFaceClient huggingFaceEmbeddingClient(){
        return new HuggingFaceClient(HF_TOKEN, Duration.ofMinutes(5), EMBEDDING_ENDPOINT);
    }

//    @Bean
//    com.corporate.riskmanagement.langchain.constructs.HuggingFaceEmbeddingModel huggingFaceEmbeddingModel() {
//        return HuggingFaceEmbeddingModel.builder().client(huggingFaceEmbeddingClient())
//                .waitForModel(true)
//                .returnFullText(true).build();
//    }

    @Bean
    dev.langchain4j.model.huggingface.HuggingFaceEmbeddingModel huggingFaceEmbeddingModelLangchain() {
        return new dev.langchain4j.model.huggingface.HuggingFaceEmbeddingModel(HF_TOKEN, EMBEDDING_MODEL, true, Duration.ofMinutes(2));
    }

    @Bean
    HuggingFaceChatLanguageModel huggingFaceChatModel() {
        return HuggingFaceChatLanguageModel.builder()
                .returnFullText(false)
                .client(huggingFaceClient())
                .build();
    }

    @Bean
    public WebMvcConfigurer corsConfigurer() {
        return new WebMvcConfigurer() {
            @Override
            public void addCorsMappings(final CorsRegistry registry) {
                registry.addMapping("/**").allowedMethods("*").allowedHeaders("*");
            }
        };
    }

}
