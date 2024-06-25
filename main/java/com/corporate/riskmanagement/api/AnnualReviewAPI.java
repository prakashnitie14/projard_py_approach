package com.corporate.riskmanagement.api;

import com.corporate.riskmanagement.domain.CompanyFinancialAnalysis;
import com.corporate.riskmanagement.dto.FileUploadResponse;
import com.corporate.riskmanagement.entities.Company;
import com.corporate.riskmanagement.entities.ExtractedFinancialEntities;
import com.corporate.riskmanagement.entities.FinancialDocument;
import com.corporate.riskmanagement.services.AiService;
import com.corporate.riskmanagement.services.AnnualReviewService;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import lombok.extern.slf4j.Slf4j;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.multipart.MultipartFile;

import java.io.IOException;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

@RestController
@Slf4j
public class AnnualReviewAPI {
    private final AnnualReviewService annualReviewService;
    private final AiService aiService;
    private ObjectMapper objectMapper;
    private final ExecutorService executorService = Executors.newFixedThreadPool(2);

    public AnnualReviewAPI(AnnualReviewService annualReviewService, AiService aiService) {
        this.annualReviewService = annualReviewService;
        this.aiService = aiService;
        this.objectMapper = new ObjectMapper();
    }

    @PostMapping("/upload")
    public FileUploadResponse uploadFileForCompany(@RequestParam String companyName, @RequestParam MultipartFile file) throws IOException {
        log.info("Uploading documents for company={}", companyName);
        FinancialDocument financialDocument = new FinancialDocument();
        Company existingCompany = annualReviewService.getCompany(companyName);
        if (existingCompany == null){
            existingCompany = annualReviewService.createCompany(new Company(companyName));
        }
        log.info("created company with id={}", existingCompany.getId());
        financialDocument.setCompany(existingCompany);
        String location = annualReviewService.uploadDocuments(financialDocument, file);
        Company finalExistingCompany = existingCompany;
        executorService.submit(() -> {
            try {
                Object response = aiService.chatWithModelUsingVectorStore(file);
                if(response instanceof CompanyFinancialAnalysis.FinancialData){
                    response = objectMapper.convertValue(response, JsonNode.class);
                }
                ExtractedFinancialEntities extractedFinancialEntities = ExtractedFinancialEntities.builder()
                        .company(finalExistingCompany)
                        .rawData((String) response).build();
                annualReviewService.persistExtractedEntities(extractedFinancialEntities);
            } catch (Exception e) {
                log.error("Error while performing analysis {}", e.getMessage());
                throw new RuntimeException(e);
            }
        });
        log.info("Successfully uploaded documents for company={}", companyName);
        return FileUploadResponse.builder().filePath(location).build();
    }

    @GetMapping("/extracted/data")
    public ExtractedFinancialEntities getExtractedEntities(@RequestParam String companyName){
        return annualReviewService.getExtractedEntities(companyName).orElse(ExtractedFinancialEntities.builder().build());
    }
}
