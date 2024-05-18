package com.corporate.riskmanagement.langchain.constructs;

import dev.langchain4j.data.embedding.Embedding;
import dev.langchain4j.data.segment.TextSegment;
import dev.langchain4j.model.embedding.EmbeddingModel;
import dev.langchain4j.model.huggingface.client.EmbeddingRequest;
import dev.langchain4j.model.huggingface.client.HuggingFaceClient;
import dev.langchain4j.model.output.Response;
import lombok.AllArgsConstructor;
import lombok.Builder;

import java.util.List;
import java.util.stream.Collectors;

@Builder
@AllArgsConstructor
public class HuggingFaceEmbeddingModel implements EmbeddingModel {
    private final HuggingFaceClient client;
    private final Double temperature;
    private final Integer maxNewTokens;
    private final Boolean returnFullText;
    private final Boolean waitForModel;


    public Response<List<Embedding>> embedAll(List<TextSegment> textSegments) {
        List<String> texts = (List)textSegments.stream().map(TextSegment::text).collect(Collectors.toList());
        return this.embedTexts(texts);
    }

    private Response<List<Embedding>> embedTexts(List<String> texts) {
        EmbeddingRequest request = new EmbeddingRequest(texts, this.waitForModel);
        List<float[]> response = this.client.embed(request);
        List<Embedding> embeddings = (List)response.stream().map(Embedding::from).collect(Collectors.toList());
        return Response.from(embeddings);
    }
}
