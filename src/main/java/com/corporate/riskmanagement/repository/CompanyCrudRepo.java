package com.corporate.riskmanagement.repository;

import com.corporate.riskmanagement.entities.Company;
import org.springframework.data.repository.CrudRepository;
import org.springframework.stereotype.Repository;

import java.util.Optional;

@Repository
public interface CompanyCrudRepo extends CrudRepository<Company, Long> {
    Optional<Company> findByName(String name);
}
