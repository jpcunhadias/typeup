-- typeup combine: the first of two filter passes (marks.lua is the second).
-- typeup writes one empty marker per note, in date order:
--   ::: {.typeup-note src="/abs/path/note.md" course="..." label="..." date="..."}
--   :::
-- Each note is read on its own and its blocks follow its marker, so
--   * its reference links ([slides]) and footnotes ([^1]) are its own,
--     however many other notes use the same names;
--   * its identifiers get a per-note prefix (note2-...), and its links to
--     #anchors in the same note follow them;
--   * its legend-* front matter applies to it only: every note starts from
--     the wording of the config file, or else of notes-header.tex.

local READER = "markdown+bracketed_spans"
local ROLES = { { "added", "addedrole" }, { "your", "yourrole" },
                { "unclear", "unclearrole" }, { "source", "sourcerole" } }

-- A metadata value as inline LaTeX
local function meta_latex(value)
  local t = pandoc.utils.type(value)
  local inlines
  if t == "Inlines" then
    inlines = value
  elseif t == "Blocks" then
    inlines = pandoc.utils.blocks_to_inlines(value)
  else
    inlines = pandoc.utils.blocks_to_inlines(pandoc.read(tostring(value), READER).blocks)
  end
  return (pandoc.write(pandoc.Pandoc({ pandoc.Plain(inlines) }), "latex"):gsub("%s+$", ""))
end

local function read_note(src)
  local f, err = io.open(src, "r")
  if not f then error("typeup combine: cannot read " .. tostring(err)) end
  local text = f:read("a")
  f:close()
  return pandoc.read(text, READER)
end

local function with_id(el, prefix, ids)
  if el.identifier and el.identifier ~= "" then
    ids[el.identifier] = true
    el.identifier = prefix .. el.identifier
    return el
  end
end

local function namespace(blocks, prefix)
  local ids = {}
  local function rename(el) return with_id(el, prefix, ids) end
  blocks = blocks:walk({
    Header = rename, Div = rename, Span = rename, CodeBlock = rename,
    Code = rename, Table = rename, Figure = rename, Image = rename, Link = rename,
  })
  return blocks:walk({
    Link = function(link)
      local id = link.target:match("^#(.+)$")
      if id and ids[id] then
        link.target = "#" .. prefix .. id
        return link
      end
    end,
  })
end

-- \renewcommand for the wording a note sets, else the saved default
local function legend_blocks(meta)
  local out = pandoc.Blocks({})
  for _, role in ipairs(ROLES) do
    local key, macro = role[1], role[2]
    local value = meta["legend-" .. key]
    if value ~= nil then
      out:insert(pandoc.RawBlock("latex",
        "\\renewcommand{\\" .. macro .. "}{" .. meta_latex(value) .. "}"))
    else
      out:insert(pandoc.RawBlock("latex", "\\let\\" .. macro .. "\\typeupdefault" .. macro))
    end
  end
  return out
end

function Pandoc(doc)
  local out, n = pandoc.Blocks({}), 0
  for _, block in ipairs(doc.blocks) do
    local src = block.t == "Div" and block.classes:includes("typeup-note")
      and block.attributes.src
    if src then
      n = n + 1
      if n == 1 then
        -- marks.lua puts the config's wording at the very top, before this
        for _, role in ipairs(ROLES) do
          out:insert(pandoc.RawBlock("latex",
            "\\let\\typeupdefault" .. role[2] .. "\\" .. role[2]))
        end
      end
      local note = read_note(src)
      block.attributes.src = nil
      out:insert(block)
      out:extend(legend_blocks(note.meta))
      out:extend(namespace(note.blocks, "note" .. n .. "-"))
    else
      out:insert(block)
    end
  end
  if n == 0 then return nil end
  doc.blocks = out
  return doc
end
