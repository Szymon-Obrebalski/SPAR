CREATE TABLE SPAR(  
    `Kod_kreskowy` varchar(13) NOT NULL,
    `Nazwa_towaru` text DEFAULT NULL,
    `Cena` float DEFAULT NULL,
    `Ilość_zamówiona` float DEFAULT NULL,
    `Wartość` float DEFAULT NULL,
    `Opcja_produktu` text DEFAULT NULL,
    `data` date NOT NULL,
    PRIMARY KEY (`Kod_kreskowy`, `data`)
)