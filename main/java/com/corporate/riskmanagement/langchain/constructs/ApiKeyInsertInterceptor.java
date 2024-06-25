package com.corporate.riskmanagement.langchain.constructs;

import dev.langchain4j.internal.ValidationUtils;
import okhttp3.Interceptor;
import okhttp3.Request;
import okhttp3.Response;

import java.io.IOException;

public class ApiKeyInsertInterceptor implements Interceptor {
        private final String apiKey;

        ApiKeyInsertInterceptor(String apiKey) {
            this.apiKey = ValidationUtils.ensureNotBlank(apiKey, "apiKey");
        }

        public Response intercept(Chain chain) throws IOException {
            Request request = chain.request().newBuilder().addHeader("Authorization", "Bearer " + this.apiKey).build();
            return chain.proceed(request);
        }

}
