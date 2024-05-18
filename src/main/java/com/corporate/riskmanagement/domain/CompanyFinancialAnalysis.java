package com.corporate.riskmanagement.domain;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import lombok.Builder;
import lombok.Data;

@Data
public class CompanyFinancialAnalysis {
    public record IncomeStatementCurrentYear(String currentYear, IncomeStatement incomeStatement) {
    }
    public record IncomeStatementPreviousYear(String previousYear, IncomeStatement incomeStatement) {
    }
    @JsonIgnoreProperties(ignoreUnknown = true)
    public record IncomeStatement(String gross_profit, String income_before_taxes, String costOfSales, String depreciation,
                                  String net_income_before_taxes, String hst_Receivable) {
    }
    @JsonIgnoreProperties(ignoreUnknown = true)
    public record IncomeStatementRecords(IncomeStatementCurrentYear incomeStatementCurrentYear, IncomeStatementPreviousYear incomeStatementPreviousYear) {
    }


    public record BalanceSheetCurrentYear(String currentYear, BalanceSheet balanceSheet) {
    }
    public record BalanceSheetPreviousYear(String previousYear, BalanceSheet balanceSheet) {
    }
    public record BalanceSheet(String total_current_assets, String total_current_liabilities) {
    }
    public record BalanceSheetRecords(BalanceSheetCurrentYear balanceSheetCurrentYear, BalanceSheetPreviousYear balanceSheetPreviousYear) {
    }

    @Builder
    public record FinancialData(String companyName, BalanceSheetRecords balanceSheet, IncomeStatementRecords incomeStatement) {
    }

}
