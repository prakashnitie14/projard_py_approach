package com.corporate.riskmanagement.services;

import com.corporate.riskmanagement.domain.CompanyFinancialAnalysis;
import org.apache.commons.io.IOUtils;
import org.junit.jupiter.api.Test;
import org.springframework.ai.parser.BeanOutputParser;

import java.io.IOException;
import java.nio.charset.StandardCharsets;


public class AiServiceTest {
    @Test
    void testParsingResponse() throws IOException {
//        String response = IOUtils.resourceToString("response.json", StandardCharsets.UTF_8);
//        BeanOutputParser<CompanyFinancialAnalysis.FinancialData> beanOutputParser = new BeanOutputParser<>(CompanyFinancialAnalysis.FinancialData.class);
//        CompanyFinancialAnalysis.FinancialData financialData = beanOutputParser.parse(response);
//        System.out.println(financialData);
    }
}