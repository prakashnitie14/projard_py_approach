package com.corporate.riskmanagement.langchain.constructs;

import com.corporate.riskmanagement.domain.CompanyFinancialAnalysis;
import dev.langchain4j.service.SystemMessage;
import dev.langchain4j.service.UserMessage;
import dev.langchain4j.service.V;

public interface FinancialDataExtractor {

    String PROMPT = "[INST] You are a financial analysis API specializing in analysing income statements and balance sheets.\n " +
            "<s> Your job is to extract structured financial data from an unstructured bank note and provide a valid JSON response.\n </s>" +
            "Give extremely precise answers to what you are asked from the information provided to you.\n" +
            "Do not provide any explanation and don't indicate the datatype in the response\n " +
            "You need to determine the current year and previous year for which the data has been presented and segregate the data according to the years. \n" +
            "DO NOT offer any explanation, strictly return only the data in JSON \n [/INST]" +
            "{information}";
    String BALANCE_SHEET_PROMPT = "Extract the following fields from the balance sheets and produce a structured, precise and VALID JSON response " +
            "Please extract the total current assets and total current liabilities, non current assets and non current liabilities, HST receivable \n" +
            "Use the below data \n" +
            "{information}";
    String INCOME_STATEMENT_PROMPT = "Extract the following fields from the income statement and produce a structured, precise and VALID JSON response \n" +
            "Please extract the income before taxes, dividends paid, depreciation and cost of sales \n" +
            "{information}";

    @SystemMessage("[INST]" + PROMPT + "[/INST]")
    @UserMessage("""
            Extract data in the below format from the income statement
            """)
    CompanyFinancialAnalysis.IncomeStatementRecords getIncomeAnalysis(@V("query") String query);
    @SystemMessage(PROMPT)
    @UserMessage("""
            Extract data in the below format from the statement of balance sheets presented in the document.
            Total current assets is the sum of all current assets. 
            Total current liabilities is the sum of all current liabilities.
            """)
    CompanyFinancialAnalysis.BalanceSheetRecords getBalanceSheetAnalysis(@V("query") String query);
}