#!/usr/bin/env bash
# weather.sh — devuelve JSON para waybar custom/weather
#   text:    emoji-clima + temperatura
#   class:   "<day|night> [rain|storm|snow|sleet|fog]? [cold]?"
#   tooltip: pango markup con info detallada (clima, viento, humedad,
#            sensación térmica, amanecer/atardecer)

LOCATION="Punto+Fijo,Venezuela"
LOCATION_PRETTY="Punto Fijo, VE"
COLD_THRESHOLD=5            # °C: por debajo de esto activa la animación "cold"
CACHE_DIR="${XDG_RUNTIME_DIR:-/tmp}/waybar-weather"
mkdir -p "$CACHE_DIR"
ASTRO_CACHE="$CACHE_DIR/astronomy"
DATA_CACHE="$CACHE_DIR/last-good"

today=$(date +%Y-%m-%d)

data=$(curl -s --max-time 8 "https://wttr.in/${LOCATION}?format=j1" 2>/dev/null)
if [[ -z "$data" ]] || ! echo "$data" | jq -e . >/dev/null 2>&1; then
    [[ -s "$DATA_CACHE" ]] && data=$(cat "$DATA_CACHE")
fi

code=""; temp=""; feels=""; humid=""; wind=""; desc=""
sunrise=""; sunset=""

if [[ -n "$data" ]]; then
    code=$(echo    "$data" | jq -r '.current_condition[0].weatherCode      // empty')
    temp=$(echo    "$data" | jq -r '.current_condition[0].temp_C           // empty')
    feels=$(echo   "$data" | jq -r '.current_condition[0].FeelsLikeC       // empty')
    humid=$(echo   "$data" | jq -r '.current_condition[0].humidity         // empty')
    wind=$(echo    "$data" | jq -r '.current_condition[0].windspeedKmph    // empty')
    desc=$(echo    "$data" | jq -r '.current_condition[0].lang_es[0].value // .current_condition[0].weatherDesc[0].value // empty')
    sunrise=$(echo "$data" | jq -r '.weather[0].astronomy[0].sunrise       // empty')
    sunset=$(echo  "$data" | jq -r '.weather[0].astronomy[0].sunset        // empty')

    if [[ -n "$code" && -n "$temp" && -n "$sunrise" && -n "$sunset" ]]; then
        echo "$data" > "$DATA_CACHE"
        printf '%s\n%s\n%s\n' "$today" "$sunrise" "$sunset" > "$ASTRO_CACHE"
    fi
fi

# Fallback a cache de astronomía si la API falló
if [[ -z "$sunrise" || -z "$sunset" ]]; then
    if [[ -s "$ASTRO_CACHE" ]]; then
        mapfile -t lines < "$ASTRO_CACHE"
        sunrise="${lines[1]:-07:10 AM}"
        sunset="${lines[2]:-06:15 PM}"
    else
        sunrise="07:10 AM"
        sunset="06:15 PM"
    fi
fi

to_min() {
    local h m ampm
    read -r h m ampm <<< "$(echo "$1" | sed 's/:/ /')"
    h=$((10#$h)); m=$((10#$m))
    [[ "$ampm" == "PM" && "$h" -lt 12 ]] && h=$((h + 12))
    [[ "$ampm" == "AM" && "$h" -eq 12 ]] && h=0
    echo $((h * 60 + m))
}

now_min=$(( $(date +%-H) * 60 + $(date +%-M) ))
sunrise_min=$(to_min "$sunrise")
sunset_min=$(to_min "$sunset")

if (( now_min < sunrise_min || now_min >= sunset_min )); then
    daypart="night"
else
    daypart="day"
fi

# Mapeo weatherCode → emoji + categoría + descripción en español
emoji=""; weather_class=""; desc_es=""
case "$code" in
    113)
        if [[ "$daypart" == "night" ]]; then emoji="🌙"; desc_es="Despejado"
        else                                  emoji="☀️"; desc_es="Soleado"; fi ;;
    116)
        if [[ "$daypart" == "night" ]]; then emoji="🌙"; desc_es="Parcialmente nublado"
        else                                  emoji="🌤️"; desc_es="Parcialmente nublado"; fi ;;
    119)              emoji="☁️";  desc_es="Nublado" ;;
    122)              emoji="☁️";  desc_es="Cubierto" ;;
    143)              emoji="🌫️"; desc_es="Bruma";          weather_class="fog" ;;
    248|260)          emoji="🌫️"; desc_es="Niebla";         weather_class="fog" ;;
    200)              emoji="⛈️"; desc_es="Tormenta eléctrica"; weather_class="storm" ;;
    386|389)          emoji="⛈️"; desc_es="Tormenta con lluvia"; weather_class="storm" ;;
    392|395)          emoji="⛈️"; desc_es="Tormenta con nieve";  weather_class="storm" ;;
    179|182|185)      emoji="🌨️"; desc_es="Llovizna helada";    weather_class="sleet" ;;
    281|284)          emoji="🌨️"; desc_es="Llovizna helada";    weather_class="sleet" ;;
    311|314|317|320)  emoji="🌨️"; desc_es="Aguanieve";          weather_class="sleet" ;;
    350|374|377)      emoji="🌨️"; desc_es="Granizo";            weather_class="sleet" ;;
    362|365)          emoji="🌨️"; desc_es="Aguanieve";          weather_class="sleet" ;;
    227)              emoji="❄️"; desc_es="Ventisca";           weather_class="snow" ;;
    230)              emoji="❄️"; desc_es="Tormenta de nieve";  weather_class="snow" ;;
    323|326)          emoji="❄️"; desc_es="Nieve ligera";       weather_class="snow" ;;
    329|332)          emoji="❄️"; desc_es="Nieve moderada";     weather_class="snow" ;;
    335|338)          emoji="❄️"; desc_es="Nieve intensa";      weather_class="snow" ;;
    368)              emoji="❄️"; desc_es="Nevada ligera";      weather_class="snow" ;;
    371)              emoji="❄️"; desc_es="Nevada intensa";     weather_class="snow" ;;
    176)              emoji="🌧️"; desc_es="Lluvia ocasional";   weather_class="rain" ;;
    263|266)          emoji="🌧️"; desc_es="Llovizna";           weather_class="rain" ;;
    293|296)          emoji="🌧️"; desc_es="Lluvia ligera";      weather_class="rain" ;;
    299|302)          emoji="🌧️"; desc_es="Lluvia moderada";    weather_class="rain" ;;
    305|308)          emoji="🌧️"; desc_es="Lluvia intensa";     weather_class="rain" ;;
    353)              emoji="🌧️"; desc_es="Chubasco ligero";    weather_class="rain" ;;
    356)              emoji="🌧️"; desc_es="Chubasco moderado";  weather_class="rain" ;;
    359)              emoji="🌧️"; desc_es="Chubasco intenso";   weather_class="rain" ;;
    *)                emoji="🌡️"; desc_es="${desc:-—}" ;;
esac
desc="$desc_es"

# Temperatura formateada
if [[ -z "$temp" ]]; then
    temp_str="--°C"
elif [[ "$temp" =~ ^- ]]; then
    temp_str="${temp}°C"
else
    temp_str="+${temp}°C"
fi

# Frío extremo: clase adicional "cold" (independiente del tipo de clima)
cold_class=""
if [[ -n "$temp" ]] && (( temp <= COLD_THRESHOLD )); then
    cold_class="cold"
fi

# Combinar todas las clases
class="$daypart"
[[ -n "$weather_class" ]] && class="$class $weather_class"
[[ -n "$cold_class"    ]] && class="$class $cold_class"

text="${emoji}  ${temp_str}"

# ── Tooltip (pango markup) ─────────────────────────────────────
# Escape para pango: &<>"'
pango_escape() {
    local s="$1"
    s=${s//&/&amp;}
    s=${s//</&lt;}
    s=${s//>/&gt;}
    echo "$s"
}

desc_e=$(pango_escape "${desc:-—}")
loc_e=$(pango_escape "$LOCATION_PRETTY")

[[ -z "$feels" ]] && feels="—"
[[ -z "$humid" ]] && humid="—"
[[ -z "$wind"  ]] && wind="—"

# Construir tooltip multilínea (\n se respeta en pango markup de waybar)
tooltip="<b>${loc_e}</b>  ·  ${desc_e}\n"
tooltip+="${emoji}  <b>${temp_str}</b>   sens. ${feels}°C\n"
tooltip+="\n"
tooltip+="💧  ${humid}%      💨  ${wind} km/h\n"
tooltip+="🌅  ${sunrise}    🌇  ${sunset}"

# ── JSON output ────────────────────────────────────────────────
json_escape() {
    local s="$1"
    s=${s//\\/\\\\}
    s=${s//\"/\\\"}
    s=${s//$'\n'/\\n}
    echo "$s"
}

text_j=$(json_escape "$text")
tooltip_j=$(json_escape "$tooltip")
class_j=$(json_escape "$class")

printf '{"text":"%s","tooltip":"%s","class":"%s"}\n' \
    "$text_j" "$tooltip_j" "$class_j"
