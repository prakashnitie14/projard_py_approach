package com.corporate.riskmanagement.langchain.constructs;

import com.corporate.riskmanagement.langchain.constructs.dto.EmbeddingRequest;
import dev.langchain4j.model.huggingface.client.TextGenerationRequest;
import dev.langchain4j.model.huggingface.client.TextGenerationResponse;
import retrofit2.Call;
import retrofit2.http.Body;
import retrofit2.http.Headers;
import retrofit2.http.POST;
import java.util.List;

public interface HuggingFaceRestAPI {
        @POST("/")
        @Headers({"Content-Type: application/json"})
        Call<List<TextGenerationResponse>> generate(@Body TextGenerationRequest var1);

        @POST("/")
        @Headers({"Content-Type: application/json"})
        Call<List<float[]>> embed(@Body EmbeddingRequest var1);
}
