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
  -- A badge/logo in the left column: place it by hand so its top lines up with the text.
  local img, href
  pandoc.walk_block(pandoc.Div(when), {
    Image = function(i) img = img or i end,
    Link = function(l) href = href or l.target end,
  })
  local left
  if img then
    left = '\\raisebox{-\\height+1.6ex}{\\includegraphics[width=1.9cm]{' ..
           quarto.project.directory .. '/' .. img.src .. '}}'
    if href then left = '\\href{' .. href .. '}{' .. left .. '}' end
  else
    left = latex(when)
  end
  return pandoc.RawBlock('latex',
    '\\noindent\\begin{minipage}[t]{0.2\\textwidth}\\small ' .. left ..
    '\\end{minipage}\\hfill\\begin{minipage}[t]{0.77\\textwidth}' .. latex(what) ..
    '\\end{minipage}\\par\\vspace{0.6em}')
end
