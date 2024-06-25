package com.corporate.riskmanagement.langchain.constructs.dto;


import lombok.Builder;
import lombok.Data;
import lombok.ToString;

import java.util.List;

@Data
@Builder
@ToString
public class EmbeddingRequest {
    private final List<String> inputs;
    private final Options options;

}
