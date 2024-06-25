package com.corporate.riskmanagement.dto;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import lombok.Builder;
import lombok.Data;

import java.util.List;

public class CompanyFinancialAnalysis {
    @JsonIgnoreProperties(ignoreUnknown = true)
    public record Statement(String grossProfit,
                                  String incomeBeforeTaxes,
                                  String costOfSales,
                                  String depreciation,
                                  String amortization,
                                  String totalExpenses,
                                  String totalSales,
                                  String interestExpense,
                                  String fiscalYear,
                                  String totalCurrentAssets,
                                  String totalCurrentLiabilities,
                                  String totalNonCurrentAssets,
                                  String totalNonCurrentLiabilities,
                                  String hstReceivable,
                                  String interestReceivable) {
    }

    @Builder
    @Data
    public static final class FinancialData {
        private final String companyName;
        private final List<Statement> statements;

    }
}
