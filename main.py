import streamlit as st
from lexer import CLexer
from parser import CParser, ASTNode
from semantic import SemanticAnalyzer
from ir import IRGenerator
from optimizer import optimize_ast
from codegen import CodeGenerator
from visualizer import (
    visualize_tokens,
    visualize_ast,
    visualize_symbol_table,
    visualize_ir,
    visualize_final_code
)

def display_ast(node, depth=0):
    if not node:
        return ""
    
    indent = "  " * depth
    result = f"{indent}- {node.type}"
    
    if node.value is not None:
        result += f": {node.value}"
    
    result += "\n"
    
    for child in node.children:
        result += display_ast(child, depth + 1)
    
    return result

def display_symbol_table(symbol_table, depth=0):
    if not symbol_table:
        return ""
    
    indent = "  " * depth
    result = f"{indent}Scope Level: {symbol_table.scope_level}\n"
    
    for name, symbol in symbol_table.symbols.items():
        result += f"{indent}  - {symbol}\n"
    
    if symbol_table.parent:
        result += f"{indent}Parent Scope:\n"
        result += display_symbol_table(symbol_table.parent, depth + 1)
    
    return result

def display_ir(ir_code):
    if not ir_code:
        return "No IR generated"
    return "\n".join(ir_code)

def display_asm(asm_code):
    if not asm_code:
        return "No assembly generated"
    return "\n".join(asm_code)

st.set_page_config(page_title="Mini C Compiler", layout="wide")
st.title("🛠️ C-like Compiler with Visual Phases")

code_input = st.text_area("📝 Enter your C-like code here:", height=300, value="""\
int add(int a, int b) {
    return a + b;
}

int main() {
    int x = 5;
    int y = 10;
    int z = add(x, y);
    
    if (z > 10) {
        z = z * 2;
    } else {
        z = z + 1;
    }
    
    return z;
}
""")

if st.button("🚀 Compile Now"):
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("🔹 Lexical Analysis")
        lexer = CLexer()
        lexer.input(code_input)
        tokens = []
        while True:
            tok = lexer.token()
            if not tok:
                break
            tokens.append(tok)
        visualize_tokens(tokens, stream=True)
        
        st.subheader("🔹 Syntax Analysis (AST)")
        parser = CParser()
        ast = parser.parse(code_input)
        
        if parser.errors:
            st.error("Parser Errors:")
            for error in parser.errors:
                st.error(error)
            st.stop()
            
        visualize_ast(ast, stream=True)
        st.text(display_ast(ast))
    
    with col2:
        if ast:
            st.subheader("🔹 Semantic Analysis")
            analyzer = SemanticAnalyzer()
            analyzer.analyze(ast)
            
            if analyzer.errors:
                st.error("Semantic Errors:")
                for error in analyzer.errors:
                    st.error(error)
                st.stop()
                
            visualize_symbol_table(analyzer.global_scope, stream=True)
            st.success("✅ Semantic analysis passed!")
            
            st.subheader("🔹 Optimization")
            optimized_ast, removed_count = optimize_ast(ast)
            st.info(f"Optimization removed {removed_count} nodes")
            visualize_ast(optimized_ast, stream=True)
            st.text(display_ast(optimized_ast))
            
            st.subheader("🔹 Intermediate Code")
            ir_generator = IRGenerator()
            ir_generator.generate(optimized_ast)
            ir_code = ir_generator.get_code()
            visualize_ir(ir_code, stream=True)
            st.text(display_ir(ir_code))
            
            st.subheader("🔹 Final Code Generation")
            code_generator = CodeGenerator(ir_code)
            asm_code = code_generator.generate()
            visualize_final_code(asm_code, stream=True)
            st.code(display_asm(asm_code), language='asm')
            
            st.success("✅ Compilation Successful!")
        else:
            st.warning("No AST generated - cannot proceed to next phases")
