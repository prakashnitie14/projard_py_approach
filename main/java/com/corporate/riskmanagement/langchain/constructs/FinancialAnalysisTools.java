package com.corporate.riskmanagement.langchain.constructs;

import dev.langchain4j.agent.tool.Tool;

public class FinancialAnalysisTools {
    static class BasicTools {
        @Tool("Retrieves data from DB")
        int stringLength(String s) {
            return s.length();
        }

        @Tool("Calculates the sum of two numbers")
        int add(int a, int b) {
            return a + b;
        }
    }
}
