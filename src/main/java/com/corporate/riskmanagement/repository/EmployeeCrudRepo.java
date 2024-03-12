package com.corporate.riskmanagement.repository;

import com.corporate.riskmanagement.entities.Employee;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;
@Repository
public interface EmployeeCrudRepo extends JpaRepository<Employee, Long> {
}
