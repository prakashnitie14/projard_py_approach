FROM mysql:latest

ENTRYPOINT ["java", "-jar", "application.jar"]