from graphviz import Digraph
import streamlit as st

def visualize_ast(ast_node, filename='ast', format='png', gui=False, stream=False):
    if ast_node is None:
        if stream:
            st.error("❌ AST is empty or invalid.")
        return None

    dot = Digraph(comment='Abstract Syntax Tree', format=format)
    dot.attr('node', shape='box', style='filled', fillcolor='lightblue')
    dot.attr('edge', color='gray40')

    counter = [0]
    
    def add_nodes_edges(node, parent_id=None):
        if node is None:
            return
            
        node_id = str(counter[0])
        counter[0] += 1
        
        if hasattr(node, 'value') and node.value is not None:
            label = f"{node.type}\n{str(node.value)}"
        else:
            label = node.type
            
        dot.node(node_id, label)
        
        if parent_id is not None:
            dot.edge(parent_id, node_id)
        
        if hasattr(node, 'children'):
            for child in node.children:
                if child is not None:
                    add_nodes_edges(child, node_id)
    
    add_nodes_edges(ast_node)
    
    if stream:
        st.subheader("🎯 Abstract Syntax Tree Visualization")
        st.graphviz_chart(dot.source)
    else:
        dot.render(filename, cleanup=True)
    
    return dot

def visualize_tokens(tokens, stream=False):
    if not tokens:
        if stream:
            st.warning("No tokens generated")
        return
        
    if stream:
        st.subheader("🧾 Tokens")
        token_data = []
        for tok in tokens:
            token_data.append({
                "Type": tok.type,
                "Value": tok.value,
                "Line": tok.lineno
            })
        st.table(token_data)

def visualize_symbol_table(symbol_table, stream=False):
    if symbol_table is None:
        if stream:
            st.warning("No symbol table available")
        return
        
    if stream:
        st.subheader("🧠 Symbol Table")
        
        def display_table(table, depth=0):
            indent = "&nbsp;" * (depth * 4)
            html = f"{indent}<b>Scope Level {table.scope_level}:</b><br>"
            
            for name, symbol in table.symbols.items():
                symbol_info = f"{indent}&nbsp;&nbsp;- {name}: {symbol.type}"
                if hasattr(symbol, 'is_function') and symbol.is_function:
                    params = ", ".join([f"{p[0]} {p[1]}" for p in symbol.parameters])
                    symbol_info += f" function({params})"
                html += symbol_info + "<br>"
            
            if table.parent:
                html += f"{indent}↳ Parent Scope:<br>"
                html += display_table(table.parent, depth + 1)
                
            return html
        
        st.markdown(display_table(symbol_table), unsafe_allow_html=True)

def visualize_ir(ir_code, stream=False):
    if not ir_code:
        if stream:
            st.warning("No IR generated")
        return
        
    if stream:
        st.subheader("⚙️ Intermediate Representation")
        st.code("\n".join(ir_code), language='text')

def visualize_final_code(code_lines, stream=False):
    if not code_lines:
        if stream:
            st.warning("No assembly generated")
        return
        
    if stream:
        st.subheader("🧩 Final Assembly Code")
        st.code("\n".join(code_lines), language='asm')