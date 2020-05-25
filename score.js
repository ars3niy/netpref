function Score_InitP()
{
    return [[0], [0], [0]];
}

function Score_InitG()
{
    return Score_InitP();
}

function Score_InitV()
{
    return [[null, [0], [0]], [[0], null, [0]], [[0], [0], null]];
}

function Score_Init()
{
    return {
        p: Score_InitP(),
        g: Score_InitG(),
        v: Score_InitV()
    };
}

function updateScore(s, value)
{
    if ((s.length == 0) || (s[s.length-1] != value))
        s.push(value);
}

function Score_UpdateP(score, p)
{
    for (var i = 0; i < p.length; i++)
        updateScore(score.p[i], p[i]);
}

function Score_UpdateG(score, g)
{
    for (var i = 0; i < g.length; i++)
        updateScore(score.g[i], g[i]);
}

function Score_UpdateV(score, v)
{
    for (var i = 0; i < v.length; i++)
        for (var j = 0; j < v[i].length; j++)
            if (j != i) {
                updateScore(score.v[i][j], v[i][j]);
            }
}

function Score_GetValue(score, area)
{
    if (area) {
        var values = null;
        if (area.parameter == "p")
            values = score.p[area.index1];
        else if (area.parameter == "g")
            values = score.g[area.index1];
        else
            values = score.v[area.index1][area.index2];
        if (values)
            return values[values.length-1];
    }

    return 0;
}

const scoreW = 600;
const scoreH = 400;
const scoreColor = "#FFFFAA";
const scoreHighlightColor = "#CCCC88";
const scoreFontSize = 20;
const scoreTopSpacing = 20;
const vWidth = 60;
const pWidth = 30;
const textGap = 5;

var pOutTop_y = vWidth;
var pOutBottom_y = scoreH - pOutTop_y;
var pOutRight_x = scoreW/2 + (scoreW/2 * (scoreH/2 - pOutTop_y))/(scoreH/2);

var pInTop_y = vWidth + pWidth;
var pInBottom_y = scoreH - pInTop_y;
var pInRight_x = scoreW/2 + (scoreW/2 * (scoreH/2 - pInTop_y))/(scoreH/2);

var gInTop_y = vWidth + 2*pWidth;
var gInBottom_y = scoreH - gInTop_y;
var gInRight_x = scoreW/2 + (scoreW/2 * (scoreH/2 - gInTop_y))/(scoreH/2);

var gRightLine1_left = pInRight_x - textGap - scoreFontSize;
var gRightLine1_top = scoreH/2 - (scoreH/2 * (gRightLine1_left - scoreW/2))/(scoreW/2);
var gRightLine1_bottom = scoreH - gRightLine1_top;

var gRightLine2_left = gRightLine1_left - textGap - scoreFontSize;
var gRightLine2_top = scoreH/2 - (scoreH/2 * (gRightLine2_left - scoreW/2))/(scoreW/2);
var gRightLine2_bottom = scoreH - gRightLine2_top;

var vSep_x = pOutRight_x/2;

function GetScoreLines(ctx, score, maxWidths)
{
    var lines = [];
    var mustTruncate = false;
    
    if (maxWidths.length > 1) {
        var lastWidth = 0;
        var lastLine = "";
        var maxWidth = maxWidths[0];
        for (var i = 0; i <= score.length-1; i++) {
            var append = "";
            if (lastLine != "")
                append = ". ";
            append += score[i];
            var appendWidth = ctx.measureText(append).width;
            if (lastWidth + appendWidth > maxWidth) {
                lines.push(lastLine);
                if (lines.length == maxWidths.length) {
                    mustTruncate = true;
                    break;
                }
                lastLine = "";
                lastWidth = 0;
                maxWidth = maxWidths[lines.length];
            }
            lastLine += append;
            lastWidth += appendWidth;
        }
        if (!mustTruncate) {
            lines.push(lastLine);
            while (lines.length < maxWidths.length)
                lines.push("");
            return lines;
        }
    }
    
    var lastWidth = 0;
    var lastLine = "";
    var lineIndex = maxWidths.length-1;
    var maxWidth = maxWidths[lineIndex];
    
    for (var i = score.length-1; i >= 0; i--) {
        var prepend = "";
        if (lastLine != "") {
            prepend = ". ";
        }
        prepend = score[i] + prepend;
        var prependWidth = ctx.measureText(prepend).width;
        if (lastWidth + prependWidth > maxWidth) {
            lines.splice(0, 0, lastLine);
            if (lines.length == maxWidths.length)
                return lines;
            lastLine = "";
            lastWidth = 0;
            lineIndex--;
            maxWidth = maxWidths[lineIndex];
        }
        lastLine = prepend + lastLine;
        lastWidth += prependWidth;
    }
    lines.splice(0, 0, lastLine);
    while (lines.length < maxWidths.length)
        lines.splice(0, 0, "");
    return lines;
}

function Score_GetArea(canvasX, canvasY)
{
    var left = (canvasWidth - scoreW)/2;
    var top = scoreTopSpacing;

    var x = canvasX - left;
    var y = canvasY - top;

    if ((x >= 0) && (x <= scoreW) && (y >= 0) && (y <= scoreH)) {
        if ((y > scoreH/2) && (y/scoreH > x/scoreW)) {
            if (y < pInBottom_y)
                return {parameter: "g", index1: 0, index2: 0};
            else if (y <= pOutBottom_y)
                return {parameter: "p", index1: 0, index2: 0};
            else {
                if (x < vSep_x)
                    return {parameter: "v", index1: 0, index2: 1};
                else
                    return {parameter: "v", index1: 0, index2: 2};
            }
        } else if ((y < scoreH/2) && (y/scoreH < 1-x/scoreW)) {
            if (y > pInTop_y)
                return {parameter: "g", index1: 1, index2: 1};
            else if (y >= pOutTop_y)
                return {parameter: "p", index1: 1, index2: 1};
            else {
                if (x < vSep_x)
                    return {parameter: "v", index1: 1, index2: 0};
                else
                    return {parameter: "v", index1: 1, index2: 2};
            }
        } else {
            if (x < pInRight_x)
                return {parameter: "g", index1: 2, index2: 2};
            else if (x <= pOutRight_x)
                return {parameter: "p", index1: 2, index2: 2};
            else {
                if (y < scoreH/2)
                    return {parameter: "v", index1: 2, index2: 1};
                else
                    return {parameter: "v", index1: 2, index2: 0};
            }
        }
    }

    return null;
}

function Score_HighlightArea(ctx, score, canvasWidth, area)
{
    Score_DrawScore(ctx, score, canvasWidth, area);
}

function Score_ClearHighlight(ctx, score, canvasWidth)
{
    Score_DrawScore(ctx, score, canvasWidth);
}

function fillHighlightArea(ctx, canvasWidth, highlight)
{
    var left = (canvasWidth - scoreW)/2;
    var top = scoreTopSpacing;

    ctx.fillStyle = scoreHighlightColor;
    if ((highlight.parameter == "g") && (highlight.index1 == 1))
        ctx.fillRect(left, top + pInTop_y, scoreW/2, scoreH/2 - pInTop_y);
    else if ((highlight.parameter == "g") && (highlight.index1 == 0))
        ctx.fillRect(left, top + scoreH/2, scoreW/2, scoreH/2 - pInTop_y);
    else if ((highlight.parameter == "g") && (highlight.index1 == 2)) {
        ctx.beginPath();
        ctx.moveTo(left + scoreW/2, top + scoreH/2);
        ctx.lineTo(left + pInRight_x, top + pInTop_y);
        ctx.lineTo(left + pInRight_x, top + pInBottom_y);
        ctx.closePath();
        ctx.fill();
    } else if ((highlight.parameter == "p") && (highlight.index1 == 0))
        ctx.fillRect(left, top + pInBottom_y, pInRight_x, pInTop_y - pOutTop_y);
    else if ((highlight.parameter == "p") && (highlight.index1 == 1))
        ctx.fillRect(left, top + pOutTop_y, pInRight_x, pInTop_y - pOutTop_y);
    else if ((highlight.parameter == "p") && (highlight.index1 == 2))
        ctx.fillRect(left + pInRight_x, top + pInTop_y, pOutRight_x - pInRight_x, pInBottom_y - pInTop_y);
    else if ((highlight.parameter == "v") && (highlight.index1 == 0) && (highlight.index2 == 1))
        ctx.fillRect(left, top + pOutBottom_y, vSep_x, scoreH - pOutBottom_y);
    else if ((highlight.parameter == "v") && (highlight.index1 == 0) && (highlight.index2 == 2))
        ctx.fillRect(left + vSep_x, top + pOutBottom_y, pOutRight_x - vSep_x, scoreH - pOutBottom_y);
    else if ((highlight.parameter == "v") && (highlight.index1 == 1) && (highlight.index2 == 0))
        ctx.fillRect(left, top, vSep_x, scoreH - pOutBottom_y);
    else if ((highlight.parameter == "v") && (highlight.index1 == 1) && (highlight.index2 == 2))
        ctx.fillRect(left + vSep_x, top, pOutRight_x - vSep_x, scoreH - pOutBottom_y);
    else if ((highlight.parameter == "v") && (highlight.index1 == 2) && (highlight.index2 == 0))
        ctx.fillRect(left + pOutRight_x, top + scoreH/2, scoreW - pOutRight_x, pOutBottom_y - scoreH/2);
    else if ((highlight.parameter == "v") && (highlight.index1 == 2) && (highlight.index2 == 1))
        ctx.fillRect(left + pOutRight_x, top + pOutTop_y, scoreW - pOutRight_x, pOutBottom_y - scoreH/2);
}

function Score_DrawScore(ctx, score, canvasWidth, highlight)
{
    Game_Debug("score.v0 " + score.v[0]);
    Game_Debug("score.v1 " + score.v[1]);
    Game_Debug("score.v2 " + score.v[2]);

    var left = (canvasWidth - scoreW)/2;
    var top = scoreTopSpacing;
    ctx.fillStyle = scoreColor;
    ctx.fillRect(left, top, scoreW, scoreH);

    if (typeof(highlight) != "undefined")
        fillHighlightArea(ctx, canvasWidth, highlight);

    ctx.strokeStyle = "black";
    ctx.strokeRect(left, top, scoreW, scoreH);
    
    ctx.moveTo(left + scoreW/2, top + scoreH/2);
    ctx.lineTo(left, top + scoreH/2);
    ctx.stroke();
    ctx.moveTo(left + scoreW/2, top + scoreH/2);
    ctx.lineTo(left + scoreW, top);
    ctx.stroke();
    ctx.moveTo(left + scoreW/2, top + scoreH/2);
    ctx.lineTo(left + scoreW, top + scoreH);
    ctx.stroke();
    
    ctx.moveTo(left, top + pOutTop_y);
    ctx.lineTo(left + pOutRight_x, top + pOutTop_y);
    ctx.lineTo(left + pOutRight_x, top + pOutBottom_y);
    ctx.lineTo(left, top + pOutBottom_y);
    ctx.stroke();
    
    ctx.moveTo(left, top + pInTop_y);
    ctx.lineTo(left + pInRight_x, top + pInTop_y);
    ctx.lineTo(left + pInRight_x, top + pInBottom_y);
    ctx.lineTo(left, top + pInBottom_y);
    ctx.stroke();
    
    ctx.moveTo(left + vSep_x, top + pOutTop_y);
    ctx.lineTo(left + vSep_x, top);
    ctx.stroke();
    ctx.moveTo(left + vSep_x, top + pOutBottom_y);
    ctx.lineTo(left + vSep_x, top + scoreH);
    ctx.stroke();
    ctx.moveTo(left + pOutRight_x, top + scoreH/2);
    ctx.lineTo(left + scoreW, top + scoreH/2);
    ctx.stroke();
    
    ctx.font = scoreFontSize + "px Arial";
    ctx.fillStyle = "black";
    ctx.textAlign = "left";
    var p0line = GetScoreLines(ctx, score.p[0], [pInRight_x - 2*textGap])[0];
    var p1line = GetScoreLines(ctx, score.p[1], [pInRight_x - 2*textGap])[0];
    var p2line = GetScoreLines(ctx, score.p[2], [pInBottom_y - pInTop_y])[0];
    var g0line = GetScoreLines(ctx, score.g[0], [gInRight_x - 2*textGap])[0];
    var g1line = GetScoreLines(ctx, score.g[1], [gInRight_x - 2*textGap])[0]; 
    var g2lines = GetScoreLines(ctx, score.g[2], [gRightLine1_bottom - gRightLine1_top,
                                                  gRightLine2_bottom - gRightLine2_top]);
    
    var v01lines = GetScoreLines(ctx, score.v[0][1], [vSep_x - 2*textGap,
                                                      vSep_x - 2*textGap]);
    var v02lines = GetScoreLines(ctx, score.v[0][1], [pOutRight_x - vSep_x - textGap,
                                                      pOutRight_x - vSep_x - textGap]);
    
    var v10lines = GetScoreLines(ctx, score.v[1][0], [vSep_x - 2*textGap,
                                                      vSep_x - 2*textGap]);
    var v12lines = GetScoreLines(ctx, score.v[1][2], [pOutRight_x - vSep_x - textGap,
                                                      pOutRight_x - vSep_x - textGap]);
    
    var v20lines = GetScoreLines(ctx, score.v[2][0], [pOutBottom_y - scoreH/2 - textGap,
                                                      pOutBottom_y - scoreH/2 - textGap]);
    var v21lines = GetScoreLines(ctx, score.v[2][1], [scoreH/2 - pOutTop_y - textGap,
                                                      scoreH/2 - pOutTop_y - textGap]);
    
    
    ctx.fillText(p0line, left + textGap, top + pOutBottom_y - (pWidth - scoreFontSize)/2);
    ctx.fillText(p1line, left + textGap, top + pInTop_y - (pWidth - scoreFontSize)/2);
    ctx.fillText(g0line, left + textGap, top + pInBottom_y - textGap);
    ctx.fillText(g1line, left + textGap, top + pInTop_y + scoreFontSize);
    
    ctx.fillText(v01lines[0], left + textGap, top + pOutBottom_y + scoreFontSize);
    ctx.fillText(v01lines[1], left + textGap, top + pOutBottom_y + 2*scoreFontSize + textGap);
    ctx.fillText(v02lines[0], left + vSep_x + textGap, top + pOutBottom_y + scoreFontSize);
    ctx.fillText(v02lines[1], left + vSep_x + textGap, top + pOutBottom_y + 2*scoreFontSize + textGap);
    
    ctx.fillText(v10lines[0], left + textGap, top + scoreFontSize);
    ctx.fillText(v10lines[1], left + textGap, top + 2*scoreFontSize + textGap);
    ctx.fillText(v12lines[0], left + vSep_x + textGap, top + scoreFontSize);
    ctx.fillText(v12lines[1], left + vSep_x + textGap, top + 2*scoreFontSize + textGap);
    
    ctx.rotate(-Math.PI/2);
    ctx.fillText(p2line, -top - pInBottom_y, left + pOutRight_x - (pOutRight_x - pInRight_x - scoreFontSize)/2);
    ctx.fillText(g2lines[0], -top - gRightLine1_bottom, left + gRightLine1_left + scoreFontSize);
    ctx.fillText(g2lines[1], -top - gRightLine2_bottom, left + gRightLine2_left + scoreFontSize);
    ctx.rotate(Math.PI/2);
}
