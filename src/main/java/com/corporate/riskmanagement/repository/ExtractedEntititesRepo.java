package com.corporate.riskmanagement.repository;

import com.corporate.riskmanagement.entities.Company;
import com.corporate.riskmanagement.entities.ExtractedFinancialEntities;
import org.springframework.data.repository.CrudRepository;

import java.util.Optional;

public interface ExtractedEntititesRepo extends CrudRepository<ExtractedFinancialEntities, Long> {
    Optional<ExtractedFinancialEntities>  findByCompany(Company company);
}
