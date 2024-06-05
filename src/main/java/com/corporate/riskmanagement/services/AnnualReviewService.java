package com.corporate.riskmanagement.services;

import com.corporate.riskmanagement.aws.PersistenceService;
import com.corporate.riskmanagement.entities.Company;
import com.corporate.riskmanagement.entities.ExtractedFinancialEntities;
import com.corporate.riskmanagement.entities.FinancialDocument;
import com.corporate.riskmanagement.entities.DocumentMetadata;
import com.corporate.riskmanagement.repository.CompanyCrudRepo;
import com.corporate.riskmanagement.repository.CompanyRiskDocumentsCrudRepo;
import com.corporate.riskmanagement.repository.DocumentMetadataCrudRepo;
import com.corporate.riskmanagement.repository.ExtractedEntititesRepo;
import lombok.AllArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.web.multipart.MultipartFile;
import software.amazon.awssdk.services.s3.model.CompleteMultipartUploadResponse;

import java.io.IOException;
import java.util.List;
import java.util.Optional;

@Service
@Slf4j
@AllArgsConstructor
public class AnnualReviewService {
    private final CompanyRiskDocumentsCrudRepo companyRiskDocumentsCrudRepo;
    private final PersistenceService persistenceService;
    private final CompanyCrudRepo companyCrudRepo;
    private final DocumentMetadataCrudRepo documentMetadataCrudRepo;
    private final ExtractedEntititesRepo extractedEntititesRepo;

    public String uploadDocuments(FinancialDocument financialDocument, MultipartFile file) throws IOException {
        CompleteMultipartUploadResponse completeMultipartUploadResponse = persistenceService.persistFile(file);
        DocumentMetadata documentMetadata = new DocumentMetadata();
        documentMetadata.setFileName(file.getOriginalFilename());
        documentMetadata.setS3Uri(completeMultipartUploadResponse.location());
        documentMetadataCrudRepo.save(documentMetadata);
        financialDocument.setDocumentMetadata(documentMetadata);
        companyRiskDocumentsCrudRepo.save(financialDocument);
        return documentMetadata.getS3Uri();
    }

    public List<Company> getCompanies(){
        return (List<Company>) companyCrudRepo.findAll();
    }

    public Company createCompany(Company company){
        return companyCrudRepo.save(company);
    }

    public Company getCompany(Long id) {
        Optional<Company> companyOptional = companyCrudRepo.findById(id);
        return companyOptional.orElse(null);
    }

    public Company getCompany(String name) {
        Optional<Company> companyOptional = companyCrudRepo.findByName(name);
        return companyOptional.orElse(null);
    }

    public ExtractedFinancialEntities persistExtractedEntities(ExtractedFinancialEntities extractedFinancialEntities){
        return extractedEntititesRepo.save(extractedFinancialEntities);
    }

    public Optional<ExtractedFinancialEntities> getExtractedEntities(String companyName){
        Optional<Company> companyOptional = companyCrudRepo.findByName(companyName);
        return extractedEntititesRepo.findByCompany(companyOptional.get());
    }
}
