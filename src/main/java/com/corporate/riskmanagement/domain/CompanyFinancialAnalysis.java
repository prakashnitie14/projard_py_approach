package com.corporate.riskmanagement.domain;

import lombok.Data;

import java.math.BigDecimal;
import java.time.LocalDate;
import java.util.List;

@Data
public class CompanyFinancialAnalysis {
    private String name;
    record BalanceSheet(BigDecimal totalCurrentAssets, BigDecimal totalCurrentLiabilities) {
    }
    record IncomeStatement(BigDecimal grossProfit, BigDecimal incomeBeforeTaxes) {
    }
    record FinancialData(LocalDate asOnDate, BalanceSheet balanceSheet, IncomeStatement incomeStatement) {
    }

    List<FinancialData> financialDataList;

}
