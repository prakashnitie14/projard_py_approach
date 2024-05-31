package com.corporate.riskmanagement.repository;

import com.corporate.riskmanagement.entities.FinancialDocument;
import org.springframework.data.repository.CrudRepository;
import org.springframework.stereotype.Repository;

@Repository
public interface CompanyRiskDocumentsCrudRepo extends CrudRepository<FinancialDocument, Long> {
}
