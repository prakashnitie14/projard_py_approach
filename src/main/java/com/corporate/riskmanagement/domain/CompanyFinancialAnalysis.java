package com.corporate.riskmanagement.domain;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import lombok.Builder;
import lombok.Data;
import lombok.ToString;

import java.util.List;

@Data
@ToString
public class CompanyFinancialAnalysis {
    @JsonIgnoreProperties(ignoreUnknown = true)
    public record IncomeStatement(String grossProfit,
                                  String incomeBeforeTaxes,
                                  String costOfSales,
                                  String depreciation,
                                  String amortization,
                                  String totalExpenses,
                                  String totalSales,
                                  String interestExpense,
                                  String financialYear) {
    }
    @JsonIgnoreProperties(ignoreUnknown = true)
    public record IncomeStatementRecords(List<IncomeStatement> incomeStatements) {
    }

    @JsonIgnoreProperties(ignoreUnknown = true)
    public record BalanceSheet(String totalCurrentAssets,
                               String totalCurrentLiabilities,
                               String totalNonCurrentAssets,
                               String totalNonCurrentLiabilities,
                               String hst_Receivable,
                               String harminizedSalesTax_Receivable,
                               String interest_Receivable,
                               String financialYear) {
    }
    @JsonIgnoreProperties(ignoreUnknown = true)
    public record BalanceSheetRecords(List<BalanceSheet> balanceSheets) {
    }

    @Builder
    public record FinancialData(String companyName, BalanceSheetRecords balanceSheet, IncomeStatementRecords incomeStatement) {
    }

}
