package com.corporate.riskmanagement.repository;

import com.corporate.riskmanagement.entities.Company;
import org.springframework.data.repository.CrudRepository;
import org.springframework.stereotype.Repository;

@Repository
public interface CompanyCrudRepo extends CrudRepository<Company, Long> {
}
