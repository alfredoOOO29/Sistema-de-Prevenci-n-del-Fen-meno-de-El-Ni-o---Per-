% ==============================================================================
% HECHOS DE PRUEBA PARA PROGRAMACIÓN LÓGICA (PROLOG)
% Permite verificar consultas interactivas, unificación y backtracking
% ==============================================================================

% Importar base de reglas
:- [el_nino_rules].

% Hechos de Regiones (Átomos)
region(tumbes).
region(piura).
region(lambayeque).
region(la_libertad).
region(lima).
region(arequipa).
region(loreto).
region(cusco).

% Regiones de la Costa Norte
region_coastal_north(tumbes).
region_coastal_north(piura).
region_coastal_north(lambayeque).
region_coastal_north(la_libertad).

% Hechos de Precipitaciones (mm)
precipitacion(tumbes, 185.5).
precipitacion(piura, 142.0).
precipitacion(lambayeque, 95.0).
precipitacion(la_libertad, 130.0).  % Caso crítico: lluvia > 120 pero temp <= 30
precipitacion(lima, 12.0).
precipitacion(arequipa, 8.5).
precipitacion(loreto, 65.0).
precipitacion(cusco, 52.0).

% Hechos de Temperatura (°C)
temperatura(tumbes, 32.5).
temperatura(piura, 31.0).
temperatura(lambayeque, 28.5).
temperatura(la_libertad, 26.0).    % 26 <= 30 -> debe ser clasificado como alto (no normal)
temperatura(lima, 22.0).
temperatura(arequipa, 19.5).
temperatura(loreto, 29.0).
temperatura(cusco, 16.0).

% Hechos en forma de términos compuestos medicion(Region, Precip, Temp)
medicion(tumbes, 185.5, 32.5).
medicion(piura, 142.0, 31.0).
medicion(lambayeque, 95.0, 28.5).
medicion(la_libertad, 130.0, 26.0).
medicion(lima, 12.0, 22.0).
medicion(arequipa, 8.5, 19.5).
medicion(loreto, 65.0, 29.0).
medicion(cusco, 52.0, 16.0).
