package com.corporate.riskmanagement.langchain.constructs;

import com.corporate.riskmanagement.domain.CompanyFinancialAnalysis;
import dev.langchain4j.service.SystemMessage;
import dev.langchain4j.service.UserMessage;
import dev.langchain4j.service.V;

public interface FinancialDataExtractor {
    @SystemMessage("You are a helpful assistant.Use the following information to answer the questions asked:")
    void setSystemMessage();
    @UserMessage("""
            You are a financial analysis API specializing in analysing balance sheets that responds in JSON.
                                     Your job is to extract structured financial data from an unstructured bank note and output the structured data in JSON.
                                     You need to determine the years for which the financial data has been presented and segregate the data according to the years.\s
                                     The JSON schema should include:
                                      {
                                         "name": "The name of the company",
                                         "financials": [
                                             {
                                                 "asOnDate": "Date for which data has been presented. For example, Dec 31st 2022",
                                                 "statementOfIncome": {
                                                     "grossProfit": "Gross profit as on date from the income statement",
                                                     "costOfSales": "Cost of sales for the year from the income statement",
                                                     "incomeBeforeTaxes": "Income before taxes for the year",
                                                 },
                                                 "balanceSheet": {
                                                     "totalcurrentassets" : "Total current assets for the year from the balance sheet",
                                                     "totalcurrentlaibilities" : "Total current liabilities for the year from the balance sheet"
                                                 }
                                             },
                                         ]
                                     }
            """)
    CompanyFinancialAnalysis getAnalysis(@V("query") String query);
}