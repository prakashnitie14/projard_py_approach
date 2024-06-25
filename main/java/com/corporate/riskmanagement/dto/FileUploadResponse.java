package com.corporate.riskmanagement.dto;

import lombok.Builder;
import lombok.Data;

@Data
@Builder
public class FileUploadResponse {
    private String filePath;
}
