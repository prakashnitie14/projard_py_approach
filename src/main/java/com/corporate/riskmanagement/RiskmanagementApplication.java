package com.corporate.riskmanagement;


import org.springframework.boot.SpringApplication;
import org.springframework.boot.actuate.autoconfigure.security.servlet.ManagementWebSecurityAutoConfiguration;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.boot.autoconfigure.domain.EntityScan;
import org.springframework.boot.autoconfigure.security.servlet.SecurityAutoConfiguration;
import org.springframework.context.annotation.ComponentScan;
import org.springframework.data.jpa.repository.config.EnableJpaRepositories;

@SpringBootApplication(exclude = {SecurityAutoConfiguration.class, ManagementWebSecurityAutoConfiguration.class})
@EnableJpaRepositories(basePackages = "com.corporate.riskmanagement.repository")
@ComponentScan(basePackages = { "com.corporate.riskmanagement" })
@EntityScan(basePackages = "com.corporate.riskmanagement.entities")
public class RiskmanagementApplication {

	public static void main(String[] args) {
		SpringApplication.run(RiskmanagementApplication.class, args);
	}


}
