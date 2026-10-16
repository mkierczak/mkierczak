-- Turn the web CV's .entry blocks (when / what / where) into a two-column LaTeX layout for the PDF.
local function latex(blocks)
  return pandoc.write(pandoc.Pandoc(blocks), 'latex'):gsub('%s+$', '')
end

function Div(el)
  if not el.classes:includes('entry') then return nil end
  local when, what
  for _, b in ipairs(el.content) do
    if b.t == 'Div' and b.classes:includes('when') then when = b.content end
    if b.t == 'Div' and b.classes:includes('what') then what = b.content end
  end
  if not (when and what) then return nil end
  return pandoc.RawBlock('latex',
    '\\noindent\\begin{minipage}[t]{0.2\\textwidth}\\small ' .. latex(when) ..
    '\\end{minipage}\\hfill\\begin{minipage}[t]{0.77\\textwidth}' .. latex(what) ..
    '\\end{minipage}\\par\\vspace{0.6em}')
end
