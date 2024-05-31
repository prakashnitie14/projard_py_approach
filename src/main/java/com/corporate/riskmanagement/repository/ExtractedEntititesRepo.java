package com.corporate.riskmanagement.repository;

import com.corporate.riskmanagement.entities.ExtractedFinancialEntities;
import org.springframework.data.repository.CrudRepository;

public interface ExtractedEntititesRepo extends CrudRepository<ExtractedFinancialEntities, Long> {
}
