package com.corporate.riskmanagement.entities;

import com.fasterxml.jackson.annotation.JsonIgnore;
import jakarta.persistence.*;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@AllArgsConstructor
@NoArgsConstructor
@Entity
public class CompanyRiskDocument {
    @Id
    @GeneratedValue(strategy = GenerationType.SEQUENCE)
    private Long riskDocsId;
    private DocumentType docType;

    @JsonIgnore
    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name="company_id", nullable=false)
    private Company company;

    @OneToOne(cascade = CascadeType.ALL)
    @JoinColumn(name = "document_metadata_doc_metadata_id", referencedColumnName = "docMetadataId")
    private DocumentMetadata documentMetadata;
}
