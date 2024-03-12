package com.corporate.riskmanagement.repository;

import com.corporate.riskmanagement.entities.DocumentMetadata;
import org.springframework.data.repository.CrudRepository;
import org.springframework.stereotype.Repository;

@Repository
public interface DocumentMetadataCrudRepo extends CrudRepository<DocumentMetadata, Long> {
}
