-- DATA CLEANING --
-- Check for duplicates
SELECT name, artist, COUNT(*) AS duplicate_count
FROM tracks 
GROUP BY name, artist 
HAVING COUNT(*) > 1;

-- Remove duplicates (if any)
DELETE FROM tracks 
WHERE ctid NOT IN (
    SELECT MIN(ctid) 
    FROM tracks 
    GROUP BY name, artist
);

-- Handle missing values
UPDATE tracks 
SET tempo = 125, energy = 0.346, danceability = 0.568, valence_proxy = 0.732 
WHERE tempo IS NULL OR energy IS NULL OR danceability IS NULL OR valence_proxy IS NULL;

-- Validate ranges
SELECT * 
FROM tracks 
WHERE tempo < 110 OR tempo > 140 
   OR energy < 0 OR energy > 1 
   OR danceability < 0 OR danceability > 1 
   OR valence_proxy < 0 OR valence_proxy > 1;

-- Fix out-of-range
UPDATE tracks 
SET tempo = CASE 
    WHEN tempo < 110 THEN 110 
    WHEN tempo > 140 THEN 140 
    ELSE tempo 
END,
energy = CASE 
    WHEN energy < 0 THEN 0 
    WHEN energy > 1 THEN 1 
    ELSE energy 
END,
danceability = CASE 
    WHEN danceability < 0 THEN 0 
    WHEN danceability > 1 THEN 1 
    ELSE danceability 
END,
valence_proxy = CASE 
    WHEN valence_proxy < 0 THEN 0 
    WHEN valence_proxy > 1 THEN 1 
    ELSE valence_proxy 
END;

-- Confirm count
SELECT COUNT(*) AS total_tracks FROM tracks;
-- Expected: 50.

-- EXPLORATORY ANALYSIS --
-- Q1: What’s the baseline vibe?
SELECT 
    ROUND(AVG(tempo)) AS avg_tempo,
    ROUND(AVG(energy)::numeric, 3) AS avg_energy,
    ROUND(AVG(danceability)::numeric, 3) AS avg_danceability,
    ROUND(AVG(valence_proxy)::numeric, 3) AS avg_valence
FROM tracks;
-- Expected: ~123 BPM, 0.346, 0.568, 0.732.

-- Q2: Peak-time crowd-pleasers
SELECT name, artist, tempo, energy, danceability, valence_proxy
FROM tracks
WHERE energy > 0.35 AND danceability > 0.7
ORDER BY danceability DESC, energy DESC;

-- Q3: Energy vs. Danceability Proportionality
-- (Correlation + slope: how much danceability rises per energy unit)
SELECT 
    ROUND(CORR(energy, danceability)::numeric, 3) AS energy_dance_corr,
    ROUND(
        (COVAR_SAMP(energy, danceability) / VAR_SAMP(energy))::numeric, 
        3
    ) AS energy_dance_slope
FROM tracks;
-- Corr: -1 to 1 (strength/direction). Slope: Danceability change per Energy unit.

-- Q4: Tempo vs. Danceability Proportionality
SELECT 
    ROUND(CORR(tempo, danceability)::numeric, 3) AS tempo_dance_corr,
    ROUND(
        (COVAR_SAMP(tempo, danceability) / VAR_SAMP(tempo))::numeric, 
        3
    ) AS tempo_dance_slope
FROM tracks;
-- Slope: Danceability change per BPM.

-- Q5: Energy vs. Valence_Proxy Proportionality
SELECT 
    ROUND(CORR(energy, valence_proxy)::numeric, 3) AS energy_valence_corr,
    ROUND(
        (COVAR_SAMP(energy, valence_proxy) / VAR_SAMP(energy))::numeric, 
        3
    ) AS energy_valence_slope
FROM tracks;
-- Slope: Valence change per Energy unit.

-- Q6: Tempo vs. Valence_Proxy Proportionality
SELECT 
    ROUND(CORR(tempo, valence_proxy)::numeric, 3) AS tempo_valence_corr,
    ROUND(
        (COVAR_SAMP(tempo, valence_proxy) / VAR_SAMP(tempo))::numeric, 
        3
    ) AS tempo_valence_slope
FROM tracks;

-- Q7: Danceability vs. Valence_Proxy Proportionality
SELECT 
    ROUND(CORR(danceability, valence_proxy)::numeric, 3) AS dance_valence_corr,
    ROUND(
        (COVAR_SAMP(danceability, valence_proxy) / VAR_SAMP(danceability))::numeric, 
        3
    ) AS dance_valence_slope
FROM tracks;

-- Q8: Top artists by energy-danceability synergy
SELECT 
    artist,
    COUNT(*) AS track_count,
    ROUND(AVG(energy)::numeric, 3) AS avg_energy,
    ROUND(AVG(danceability)::numeric, 3) AS avg_danceability,
    ROUND(CORR(energy, danceability)::numeric, 3) AS energy_dance_corr
FROM tracks
GROUP BY artist
HAVING COUNT(*) > 1
ORDER BY avg_danceability DESC, avg_energy DESC;

-- Q9: Tempo distribution with danceability impact
SELECT 
    CASE 
        WHEN tempo <= 122 THEN 'Slow (110-122)'
        WHEN tempo <= 126 THEN 'Mid (123-126)'
        ELSE 'Fast (127-140)'
    END AS tempo_range,
    COUNT(*) AS track_count,
    ROUND(AVG(danceability)::numeric, 3) AS avg_danceability,
    ROUND(AVG(valence_proxy)::numeric, 3) AS avg_valence
FROM tracks
GROUP BY tempo_range
ORDER BY tempo_range;

-- Q10: Sunrise set picks with valence-energy balance
SELECT name, artist, tempo, energy, danceability, valence_proxy
FROM tracks
WHERE valence_proxy > 0.8 AND tempo BETWEEN 120 AND 125
ORDER BY valence_proxy DESC, energy DESC
LIMIT 5;

-- Q11: Artists with widest mood-energy swing
SELECT 
    artist,
    COUNT(*) AS track_count,
    ROUND(MIN(energy)::numeric, 3) AS min_energy,
    ROUND(MAX(energy)::numeric, 3) AS max_energy,
    ROUND((MAX(energy) - MIN(energy))::numeric, 3) AS energy_range,
    ROUND(MIN(valence_proxy)::numeric, 3) AS min_valence,
    ROUND(MAX(valence_proxy)::numeric, 3) AS max_valence,
    ROUND((MAX(valence_proxy) - MIN(valence_proxy))::numeric, 3) AS valence_range
FROM tracks
GROUP BY artist
HAVING COUNT(*) > 1
ORDER BY energy_range DESC, valence_range DESC;

-- Q12: Optimal opener (tempo 120-123, high valence, decent groove)
SELECT name, artist, tempo, energy, danceability, valence_proxy
FROM tracks
WHERE tempo BETWEEN 120 AND 123 
  AND valence_proxy > 0.75 
  AND danceability > 0.6
ORDER BY valence_proxy DESC, danceability DESC
LIMIT 1;