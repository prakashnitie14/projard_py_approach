package com.corporate.riskmanagement.repository;

import com.corporate.riskmanagement.entities.CompanyRiskDocument;
import org.springframework.data.repository.CrudRepository;
import org.springframework.stereotype.Repository;

@Repository
public interface CompanyRiskDocumentsCrudRepo extends CrudRepository<CompanyRiskDocument, Long> {
}
