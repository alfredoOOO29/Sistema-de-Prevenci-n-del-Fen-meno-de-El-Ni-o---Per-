% ==============================================================================
% BASE DE CONOCIMIENTO Y MOTOR DE INFERENCIA LÓGICA (PROLOG)
% Sistema de Prevención del Fenómeno de El Niño - Perú
% Curso: Lenguajes de Programación - Unidad 2: Programación Lógica
% ==============================================================================

% Predicados dinámicos para permitir aserción y retracción en tiempo de ejecución
:- dynamic region/1.
:- dynamic region_coastal_north/1.
:- dynamic precipitacion/2.
:- dynamic temperatura/2.
:- dynamic medicion/3.

% ------------------------------------------------------------------------------
% 1. DEFINICIÓN DE UMBRALES (Constantes y Predicados Base)
% ------------------------------------------------------------------------------
umbral_precipitacion_extremo(120.0).
umbral_temperatura_extremo(30.0).
umbral_precipitacion_alto(80.0).
umbral_precipitacion_moderado(40.0).

% ------------------------------------------------------------------------------
% 2. REGLAS DE CLASIFICACIÓN DE RIESGO HIDROMETEOROLÓGICO
% Demostración de control de flujo con el operador de corte (!)
% y resolución determinista sin solapamientos ni lagunas lógicas.
% ------------------------------------------------------------------------------

% Validación de entrada física
clasificar_riesgo(P, _, invalido) :- P < 0.0, !.
clasificar_riesgo(P, _, invalido) :- P > 1500.0, !.
clasificar_riesgo(_, T, invalido) :- (T < -40.0 ; T > 60.0), !.

% Regla 1: Riesgo Extremo
% Lluvia torrencial (>120mm) AND temperatura elevada (>30°C)
clasificar_riesgo(P, T, extremo) :-
    umbral_precipitacion_extremo(P_Ext),
    umbral_temperatura_extremo(T_Ext),
    P > P_Ext,
    T > T_Ext,
    !.

% Regla 2: Riesgo Alto (Corrección del defecto de la versión previa)
% Lluvia torrencial (>120mm) aunque la temperatura sea moderada (<=30°C)
clasificar_riesgo(P, _, alto) :-
    umbral_precipitacion_extremo(P_Ext),
    P > P_Ext,
    !.

% Regla 3: Riesgo Alto estándar (80mm < P =< 120mm)
clasificar_riesgo(P, _, alto) :-
    umbral_precipitacion_alto(P_Alto),
    umbral_precipitacion_extremo(P_Ext),
    P > P_Alto,
    P =< P_Ext,
    !.

% Regla 4: Riesgo Moderado (40mm < P =< 80mm)
clasificar_riesgo(P, _, moderado) :-
    umbral_precipitacion_moderado(P_Mod),
    umbral_precipitacion_alto(P_Alto),
    P > P_Mod,
    P =< P_Alto,
    !.

% Regla 5: Riesgo Normal (0mm =< P =< 40mm)
clasificar_riesgo(P, _, normal) :-
    umbral_precipitacion_moderado(P_Mod),
    P >= 0.0,
    P =< P_Mod,
    !.

% ------------------------------------------------------------------------------
% 3. INFERENCIA Y EVALUACIÓN DE REGIONES
% Relaciona hechos de mediciones con niveles de riesgo
% ------------------------------------------------------------------------------

% Evaluar por predicado compuesto medicion(Region, Precip, Temp)
evaluar_medicion(Region, Riesgo) :-
    medicion(Region, P, T),
    clasificar_riesgo(P, T, Riesgo).

% Evaluar por predicados individuales precipitacion/2 y temperatura/2
evaluar_region(Region, Riesgo) :-
    precipitacion(Region, P),
    temperatura(Region, T),
    clasificar_riesgo(P, T, Riesgo).

% ------------------------------------------------------------------------------
% 4. OPERACIONES SOBRE ESTRUCTURAS DE DATOS (LISTAS Y RECURSIÓN)
% Unidad 2: Demostración de listas, recursión, backtracking y orden superior
% ------------------------------------------------------------------------------

% Caso base: longitud de lista vacía
longitud_lista([], 0).
% Caso recursivo: longitud de lista
longitud_lista([_|Resto], N) :-
    longitud_lista(Resto, NResto),
    N is NResto + 1.

% Filtrar regiones con riesgo específico de una lista dada
filtrar_por_riesgo([], _, []).
filtrar_por_riesgo([R|Resto], RiesgoBuscado, [R|Resultado]) :-
    evaluar_region(R, RiesgoBuscado),
    !,
    filtrar_por_riesgo(Resto, RiesgoBuscado, Resultado).
filtrar_por_riesgo([_|Resto], RiesgoBuscado, Resultado) :-
    filtrar_por_riesgo(Resto, RiesgoBuscado, Resultado).

% Consulta declarativa de todas las regiones con determinado nivel de riesgo
obtener_regiones_en_riesgo(NivelRiesgo, Regiones) :-
    findall(R, evaluar_region(R, NivelRiesgo), Regiones).

% Consulta de todas las regiones vulnerables (cualquier riesgo superior a normal)
obtener_todas_vulnerables(ListaVulnerables) :-
    findall(Region-Riesgo, 
            (evaluar_region(Region, Riesgo), Riesgo \= normal, Riesgo \= invalido), 
            ListaVulnerables).

% Totalizar zonas vulnerables
contar_zonas_vulnerables(Total) :-
    obtener_todas_vulnerables(Lista),
    longitud_lista(Lista, Total).
