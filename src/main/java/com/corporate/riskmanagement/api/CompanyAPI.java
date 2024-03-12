package com.corporate.riskmanagement.api;

import com.corporate.riskmanagement.entities.Company;
import com.corporate.riskmanagement.services.AnnualReviewService;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@Slf4j
public class CompanyAPI {
    @Autowired
    private AnnualReviewService annualReviewService;

    @PostMapping("/companies/create")
    public void createCompany(@RequestBody Company company){
        Company company1 = annualReviewService.createCompany(company);
        log.info("create company with id={}", company1.getId());
    }

    @GetMapping("/company")
    public Company getCompany(@RequestParam Long id){
        Company company1 = annualReviewService.getCompany(id);
        log.info("Got company with id={}", company1.getId());
        return company1;
    }

    @GetMapping("/companies")
    public List<Company> getAllCompanies(){
        return annualReviewService.getCompanies();
    }
}
