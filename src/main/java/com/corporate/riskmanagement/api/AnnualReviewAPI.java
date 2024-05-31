package com.corporate.riskmanagement.api;

import com.corporate.riskmanagement.entities.Company;
import com.corporate.riskmanagement.entities.ExtractedFinancialEntities;
import com.corporate.riskmanagement.entities.FinancialDocument;
import com.corporate.riskmanagement.services.AiService;
import com.corporate.riskmanagement.services.AnnualReviewService;
import lombok.AllArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

import java.io.IOException;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

@RestController
@Slf4j
@AllArgsConstructor
public class AnnualReviewAPI {
    private final AnnualReviewService annualReviewService;
    private final AiService aiService;
    private final ExecutorService executorService = Executors.newFixedThreadPool(2);

    @PostMapping("/upload")
    public void uploadFileForCompany(@RequestParam String companyName,@RequestParam MultipartFile file) throws IOException {
        log.info("Uploading documents for company={}", companyName);
        FinancialDocument financialDocument = new FinancialDocument();
        Company existingCompany = annualReviewService.getCompany(companyName);
        if (existingCompany == null){
            existingCompany = annualReviewService.createCompany(new Company(companyName));
        }
        log.info("created company with id={}", existingCompany.getId());
        financialDocument.setCompany(existingCompany);
        annualReviewService.uploadDocuments(financialDocument, file);
        Company finalExistingCompany = existingCompany;
        executorService.submit(() -> {
            try {
                String response = aiService.chatWithModelUsingVectorStore(file);
                ExtractedFinancialEntities extractedFinancialEntities = ExtractedFinancialEntities.builder()
                        .company(finalExistingCompany)
                        .rawData(response).build();
                annualReviewService.persistExtractedEntities(extractedFinancialEntities);
            } catch (Exception e) {
                log.error("Error while performing analysis {}", e.getMessage());
                throw new RuntimeException(e);
            }
        });
        log.info("Successfully uploaded documents for company={}", companyName);
    }
}
