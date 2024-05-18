package com.corporate.riskmanagement.langchain.constructs.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@AllArgsConstructor
@NoArgsConstructor
@Builder
public class Options {
    private Boolean waitForModel;
    private Boolean useCache;
}
