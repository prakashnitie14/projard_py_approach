package com.corporate.riskmanagement.api;

import com.corporate.riskmanagement.entities.CompanyRiskDocument;
import com.corporate.riskmanagement.entities.DocumentType;
import com.corporate.riskmanagement.services.AnnualReviewService;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

import java.io.IOException;

@RestController
@Slf4j
public class AnnualReviewAPI {
    @Autowired
    private AnnualReviewService annualReviewService;

    @PostMapping("/upload")
    public void uploadFileForCompany(@RequestParam Long companyId,@RequestParam String docType,@RequestParam MultipartFile file) throws IOException {
        log.info("Uploading documents for companyId={}", companyId);
        CompanyRiskDocument companyRiskDocument = new CompanyRiskDocument();
        companyRiskDocument.setDocType(DocumentType.valueOf(docType));
        companyRiskDocument.setCompany(annualReviewService.getCompany(companyId));
        annualReviewService.uploadDocuments(companyRiskDocument, file);
    }
}
