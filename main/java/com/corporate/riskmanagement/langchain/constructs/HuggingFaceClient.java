package com.corporate.riskmanagement.langchain.constructs;

import com.corporate.riskmanagement.langchain.constructs.dto.EmbeddingRequest;
import com.corporate.riskmanagement.langchain.constructs.dto.Options;
import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.DeserializationFeature;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.SerializationFeature;
import com.google.gson.ExclusionStrategy;
import com.google.gson.FieldNamingPolicy;
import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import dev.langchain4j.model.huggingface.client.TextGenerationRequest;
import dev.langchain4j.model.huggingface.client.TextGenerationResponse;
import lombok.extern.slf4j.Slf4j;
import okhttp3.OkHttpClient;
import org.apache.hc.client5.http.impl.classic.HttpClients;
import org.springframework.core.ParameterizedTypeReference;
import org.springframework.http.HttpHeaders;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.http.client.HttpComponentsClientHttpRequestFactory;
import org.springframework.http.converter.json.GsonHttpMessageConverter;
import org.springframework.http.converter.json.MappingJackson2HttpMessageConverter;
import org.springframework.web.client.RestClient;
import retrofit2.Response;
import retrofit2.Retrofit;
import retrofit2.converter.gson.GsonConverterFactory;

import java.io.FileWriter;
import java.io.IOException;
import java.time.Duration;
import java.util.List;

@Slf4j
public class HuggingFaceClient implements dev.langchain4j.model.huggingface.client.HuggingFaceClient {
    private final HuggingFaceRestAPI huggingFaceApi;
    private RestClient restClient;
    private ObjectMapper objectMapper = new ObjectMapper();

    public HuggingFaceClient(String apiKey, Duration timeout, String baseUrl) {
        OkHttpClient okHttpClient = (new OkHttpClient.Builder()).addInterceptor(new ApiKeyInsertInterceptor(apiKey)).callTimeout(timeout)
                .connectTimeout(timeout)
                .readTimeout(timeout)
                .writeTimeout(timeout).build();
        Gson gson = (new GsonBuilder()).setFieldNamingPolicy(FieldNamingPolicy.LOWER_CASE_WITH_UNDERSCORES).create();
        HttpComponentsClientHttpRequestFactory requestFactory = new HttpComponentsClientHttpRequestFactory();
        requestFactory.setConnectionRequestTimeout(timeout);
        requestFactory.setHttpClient(HttpClients.custom().build());
        objectMapper.configure(SerializationFeature.FAIL_ON_EMPTY_BEANS, false);
        objectMapper.enable(DeserializationFeature.UNWRAP_SINGLE_VALUE_ARRAYS);
        objectMapper.enable(DeserializationFeature.ACCEPT_EMPTY_ARRAY_AS_NULL_OBJECT);
        objectMapper.enable(DeserializationFeature.UNWRAP_ROOT_VALUE);
        restClient = RestClient.builder().baseUrl(baseUrl)
                .defaultHeaders(headers -> {
                    headers.add(HttpHeaders.CONTENT_TYPE, MediaType.APPLICATION_JSON_VALUE);
                    headers.add("Authorization", "Bearer " + apiKey);
                })
                .messageConverters(httpMessageConverters -> {
                    httpMessageConverters.add(new GsonHttpMessageConverter(gson));
                    httpMessageConverters.add(new MappingJackson2HttpMessageConverter(objectMapper));
                })
                .requestFactory(requestFactory)
                .build();
        Retrofit retrofit = (new Retrofit.Builder()).baseUrl(baseUrl).client(okHttpClient).addConverterFactory(GsonConverterFactory.create(gson)).build();
        this.huggingFaceApi = retrofit.create(HuggingFaceRestAPI.class);
    }

    public TextGenerationResponse chat(TextGenerationRequest request) {
        return this.generate(request);
    }

    public TextGenerationResponse generate(TextGenerationRequest request) {
        try {
            log.info("Sending request to generate text={}", request);
            Response<List<TextGenerationResponse>> retrofitResponse = this.huggingFaceApi.generate(request).execute();
            log.info("Retrofit response from API={}", retrofitResponse.body().get(0).generatedText());
            if (retrofitResponse.isSuccessful()) {
                return toOneResponse(retrofitResponse);
            } else {
                log.info("Return status code={}", retrofitResponse.code());
                throw toException(retrofitResponse);
            }
        } catch (IOException var3) {
            throw new RuntimeException(var3);
        }
    }

    @Override
    public List<float[]> embed(dev.langchain4j.model.huggingface.client.EmbeddingRequest embeddingRequest) {
        return embed(EmbeddingRequest.builder().inputs(embeddingRequest.getInputs()).options(Options.builder().waitForModel(true).build()).build());
    }

    private static TextGenerationResponse toOneResponse(Response<List<TextGenerationResponse>> retrofitResponse) {
        List<TextGenerationResponse> responses = retrofitResponse.body();
        if (responses != null && responses.size() == 1) {
            return (TextGenerationResponse)responses.get(0);
        } else {
            throw new RuntimeException("Expected only one generated_text, but was: " + (responses == null ? 0 : responses.size()));
        }
    }

    public List<float[]> embed(EmbeddingRequest request) {
        try {
            log.info("Inputs size={}", request.getInputs().size());
            objectMapper.writerWithDefaultPrettyPrinter().writeValue(new FileWriter("input.json"),request);
            log.info("Sending request to embedding client");
            ResponseEntity<List<List<List<float[]>>>> responseEntity = restClient.post().body(request).retrieve().toEntity(new ParameterizedTypeReference<>() {
            });
            log.info("Response status={}", responseEntity.getStatusCode());
            log.info("Response body 1={}", responseEntity.getBody().get(0).size());
            log.info("Response body 2={}" ,responseEntity.getBody().get(0).get(0).size());
            log.info("Response body 3={}" ,responseEntity.getBody().get(0).get(0).get(0));
            if(responseEntity.getStatusCode().is2xxSuccessful()){
                return responseEntity.getBody().get(0).get(0);
            }
//            Response<List<float[]>> retrofitResponse = this.huggingFaceApi.embed(request).execute();
//            if (retrofitResponse.isSuccessful()) {
//                return retrofitResponse.body();
//            } else {
//                log.info("Retrofit response={}", retrofitResponse);
//                throw toException(retrofitResponse);
//            }
        } catch (Exception var3) {
            throw new RuntimeException(var3);
        }
        return null;
    }

    private static RuntimeException toException(Response<?> response) throws IOException {
        int code = response.code();
        String body = response.errorBody().string();
        String errorMessage = String.format("status code: %s; body: %s", code, body);
        return new RuntimeException(errorMessage);
    }
}
