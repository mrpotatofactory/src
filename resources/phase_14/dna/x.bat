@echo off
SET CMD=python C:\Users\Usuario\workspace\libpandadna\compiler\compile.py --path ../..
SET CMD=%CMD% ../../phase_4/dna/storage.dna ../../phase_5/dna/storage_town.dna stor*.dna funny_farm_*.dna outdoor_zone_6100.dna
%CMD%
