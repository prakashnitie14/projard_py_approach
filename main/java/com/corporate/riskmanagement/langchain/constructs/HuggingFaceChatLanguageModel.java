package com.corporate.riskmanagement.langchain.constructs;

import dev.langchain4j.data.message.AiMessage;
import dev.langchain4j.data.message.ChatMessage;
import dev.langchain4j.model.chat.ChatLanguageModel;
import dev.langchain4j.model.huggingface.client.HuggingFaceClient;
import dev.langchain4j.model.huggingface.client.*;
import dev.langchain4j.model.output.Response;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.extern.slf4j.Slf4j;

import java.util.List;
import java.util.stream.Collectors;

@Slf4j
@Builder
@AllArgsConstructor
public class HuggingFaceChatLanguageModel implements ChatLanguageModel {
    private final HuggingFaceClient client;
    private final Double temperature;
    private final Integer maxNewTokens;
    private final Boolean returnFullText;
    private final Boolean waitForModel;

    public Response<AiMessage> generate(List<ChatMessage> messages) {
        TextGenerationRequest request = TextGenerationRequest.builder()
                .inputs((String)messages.stream().map(ChatMessage::text).collect(Collectors.joining("\n")))
                .parameters(Parameters.builder()
                        .topK(5)
                        .maxNewTokens(1000)
                        .returnFullText(false)
                        .build())
                .options(Options.builder()
                        .waitForModel(this.waitForModel).build()).build();
        TextGenerationResponse textGenerationResponse = this.client.chat(request);
        log.info("Text generation response={}", textGenerationResponse.generatedText());
        log.info("AiMessage = {}", AiMessage.from(textGenerationResponse.generatedText()).text());
        Response<AiMessage> response = Response.from(AiMessage.from(textGenerationResponse.generatedText()));
        log.info("Response={}", response);
        return response;
    }

}
