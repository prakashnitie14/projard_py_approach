package com.corporate.riskmanagement.api;

import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.*;

class DocumentAPITest {

    @BeforeEach
    void setUp() {
    }

    @AfterEach
    void tearDown() {
    }

    @Test
    void chatWithModelUsingEmbeddingStore() {
        String response = "```json\n" +
                "{\n" +
                "  \"incomeStatementCurrentYear\": {\n" +
                "    \"currentYear\": \"2023\",\n" +
                "    \"incomeStatement\": {\n" +
                "      \"costOfSales\": \"$584,646.03\",\n" +
                "      \"depreciation\": \"$9,948\",\n" +
                "      \"gross_profit\": \"$423,364.37\",\n" +
                "      \"hst_Receivable\": \"$78,267\",\n" +
                "      \"income_before_taxes\": \"$356,548.37\",\n" +
                "      \"net_Earnings_Before_Taxes\": \"$266,559\"\n" +
                "    }\n" +
                "  },\n" +
                "  \"incomeStatementPreviousYear\": {\n" +
                "    \"previousYear\": \"2022\",\n" +
                "    \"incomeStatement\": {\n" +
                "      \"costOfSales\": \"$1,961,225.28\",\n" +
                "      \"depreciation\": \"$9,644\",\n" +
                "      \"gross_profit\": \"$217,913.92\",\n" +
                "      \"hst_Receivable\": \"$69,113\",\n" +
                "      \"income_before_taxes\": \"$132,642.92\",\n" +
                "      \"net_Earnings_Before_Taxes\": \"$96,198\"\n" +
                "    }\n" +
                "  }\n" +
                "}\n" +
                "```";
        response = response.substring(7,response.lastIndexOf("```"));
        System.out.println(response);
    }
}