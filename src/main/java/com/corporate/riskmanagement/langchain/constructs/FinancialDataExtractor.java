package com.corporate.riskmanagement.langchain.constructs;

import com.corporate.riskmanagement.domain.CompanyFinancialAnalysis;
import dev.langchain4j.service.SystemMessage;
import dev.langchain4j.service.UserMessage;
import dev.langchain4j.service.V;

public interface FinancialDataExtractor {

    @SystemMessage("<s>[INST] You are a financial analysis API specializing in analysing income statements.\n [/INST]" +
            "Your job is to extract structured financial data from an unstructured bank note and output the structured data.\n </s>" +
            "Give precise answers to what you are asked from the information provided to you.\n" +
            "If you are unable to find the value, return null and DO NOT offer any explanation \n" +
            "You need to determine the years for which the financial data has been presented and segregate the data according to the years.")

    @UserMessage("""
            [INST] Extract data in the below format from the income statement [/INST]
            """)
    CompanyFinancialAnalysis.IncomeStatementRecords getIncomeAnalysis(@V("query") String query);
    @SystemMessage("You are a financial analysis API specializing in analysing balance sheets that responds only in JSON.\n" +
            "Your job is to extract structured financial data from an unstructured bank note and output the structured data in JSON.\n" +
            "Give precise answers to what you are asked, and from the information provided to you.\n" +
            "If you are unable to find the value, return null and be very concise in your response" +
            "You need to determine the years for which the financial data has been presented and segregate the data according to the years. Use the following information to answer the questions asked:")

    @UserMessage("""
            Extract the below data from the combined statement of balance sheets presented in the document
            """)
    CompanyFinancialAnalysis.BalanceSheetRecords getBalanceSheetAnalysis(@V("query") String query);
}