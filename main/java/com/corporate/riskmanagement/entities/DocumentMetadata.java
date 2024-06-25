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
public class DocumentMetadata {
    @Id
    @GeneratedValue(strategy = GenerationType.SEQUENCE)
    private Long docMetadataId;
    @Column
    private String s3Uri;
    @Column
    private String fileName;

    @JsonIgnore
    @OneToOne(mappedBy = "documentMetadata")
    private FinancialDocument financialDocument;

}
