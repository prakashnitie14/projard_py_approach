package com.corporate.riskmanagement.entities;


import jakarta.persistence.*;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;
import org.hibernate.annotations.Cascade;
import org.hibernate.annotations.CascadeType;

@Entity
@Data
@AllArgsConstructor
@NoArgsConstructor
public class Address {
    @Id
    @GeneratedValue(strategy = GenerationType.SEQUENCE)
    private Long id;

    private String line1;
    private String line2;
    private String line3;
    private String line4;
    private String line5;

    @OneToOne(fetch = FetchType.LAZY)
    @Cascade(CascadeType.PERSIST)
    private Employee employee;
}
