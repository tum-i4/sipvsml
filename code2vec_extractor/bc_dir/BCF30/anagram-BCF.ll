; ModuleID = 'anagram-BCF.bc'
source_filename = "/home/sip/sip-metadata-recovery/dataset/simple-source/anagram.c"
target datalayout = "e-m:e-p270:32:32-p271:32:32-p272:64:64-i64:64-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-linux-gnu"

@.str = private unnamed_addr constant [29 x i8] c"\22%s\22 and \22%s\22 are anagrams.\0A\00", align 1
@.str.1 = private unnamed_addr constant [33 x i8] c"\22%s\22 and \22%s\22 are not anagrams.\0A\00", align 1
@x = common global i32 0
@y = common global i32 0
@x.1 = common global i32 0
@y.2 = common global i32 0
@x.3 = common global i32 0
@y.4 = common global i32 0
@x.5 = common global i32 0
@y.6 = common global i32 0
@x.7 = common global i32 0
@y.8 = common global i32 0

; Function Attrs: noinline nounwind optnone uwtable
define i32 @main(i32 %0, i8** %1) #0 !input_indep_function !3 {
  %3 = alloca i32, align 4, !input_indep_block !4, !input_dep_instr !5, !data_dep_instr !6
  %4 = alloca i32, align 4, !input_dep_instr !5, !data_dep_instr !6
  %5 = alloca i8**, align 8, !input_dep_instr !5, !data_dep_instr !6
  %6 = alloca i8*, align 8, !input_dep_instr !5, !data_dep_instr !6
  %7 = alloca i8*, align 8, !input_dep_instr !5, !data_dep_instr !6
  %8 = alloca i32, align 4, !input_dep_instr !5, !data_dep_instr !6
  %9 = alloca i64, align 8, !input_dep_instr !5, !data_dep_instr !6
  store i32 0, i32* %3, align 4, !input_indep_instr !7, !data_indep_instr !8
  store i32 %0, i32* %4, align 4, !input_dep_instr !5, !data_dep_instr !6, !argument_dep_instr !9
  store i8** %1, i8*** %5, align 8, !input_dep_instr !5, !data_dep_instr !6, !argument_dep_instr !9
  %10 = load i32, i32* %4, align 4, !input_dep_instr !5, !data_dep_instr !6, !argument_dep_instr !9
  %11 = icmp slt i32 %10, 3, !input_dep_instr !5, !data_dep_instr !6, !argument_dep_instr !9
  br i1 %11, label %12, label %13, !input_dep_instr !5, !data_dep_instr !6, !argument_dep_instr !9

12:                                               ; preds = %2
  store i32 1, i32* %3, align 4, !data_indep_instr !8, !argument_dep_instr !9, !input_dep_block !10, !control_dep_instr !11
  br label %60, !data_indep_instr !8, !argument_dep_instr !9, !control_dep_instr !11

13:                                               ; preds = %2
  %14 = load i32, i32* @x, align 4
  %15 = load i32, i32* @y, align 4
  %16 = sub i32 %14, 1
  %17 = mul i32 %14, %16
  %18 = urem i32 %17, 2
  %19 = icmp eq i32 %18, 0
  %20 = icmp slt i32 %15, 10
  %21 = or i1 %19, %20
  br i1 %21, label %originalBB, label %originalBBalteredBB

originalBB:                                       ; preds = %13, %originalBBalteredBB
  %22 = load i8**, i8*** %5, align 8, !data_dep_instr !6, !argument_dep_instr !9, !input_dep_block !10, !control_dep_instr !11
  %23 = getelementptr inbounds i8*, i8** %22, i64 1, !data_dep_instr !6, !argument_dep_instr !9, !control_dep_instr !11
  %24 = load i8*, i8** %23, align 8, !data_dep_instr !6, !argument_dep_instr !9, !control_dep_instr !11
  store i8* %24, i8** %6, align 8, !data_dep_instr !6, !argument_dep_instr !9, !control_dep_instr !11
  %25 = load i8**, i8*** %5, align 8, !data_dep_instr !6, !argument_dep_instr !9, !control_dep_instr !11
  %26 = getelementptr inbounds i8*, i8** %25, i64 2, !data_dep_instr !6, !argument_dep_instr !9, !control_dep_instr !11
  %27 = load i8*, i8** %26, align 8, !data_dep_instr !6, !argument_dep_instr !9, !control_dep_instr !11
  store i8* %27, i8** %7, align 8, !data_dep_instr !6, !argument_dep_instr !9, !control_dep_instr !11
  %28 = load i8*, i8** %6, align 8, !data_dep_instr !6, !argument_dep_instr !9, !control_dep_instr !11
  %29 = load i8*, i8** %7, align 8, !data_dep_instr !6, !argument_dep_instr !9, !control_dep_instr !11
  %30 = call i32 @check_anagram(i8* %28, i8* %29), !data_indep_instr !8, !argument_dep_instr !9, !control_dep_instr !11
  store i32 %30, i32* %8, align 4, !data_indep_instr !8, !argument_dep_instr !9, !control_dep_instr !11
  %31 = load i32, i32* %8, align 4, !data_indep_instr !8, !argument_dep_instr !9, !control_dep_instr !11
  %32 = icmp eq i32 %31, 1, !data_indep_instr !8, !argument_dep_instr !9, !control_dep_instr !11
  %33 = load i32, i32* @x, align 4
  %34 = load i32, i32* @y, align 4
  %35 = sub i32 %33, 1
  %36 = mul i32 %33, %35
  %37 = urem i32 %36, 2
  %38 = icmp eq i32 %37, 0
  %39 = icmp slt i32 %34, 10
  %40 = or i1 %38, %39
  br i1 %40, label %originalBBpart2, label %originalBBalteredBB

originalBBpart2:                                  ; preds = %originalBB
  br i1 %32, label %41, label %42, !data_indep_instr !8, !argument_dep_instr !9, !control_dep_instr !11

41:                                               ; preds = %originalBBpart2
  call void @main0(i8** %7, i8** %6), !data_indep_instr !8, !argument_dep_instr !9, !input_dep_block !10, !control_dep_instr !11
  br label %43, !data_indep_instr !8, !argument_dep_instr !9, !control_dep_instr !11

42:                                               ; preds = %originalBBpart2
  call void @main1(i8** %7, i8** %6), !data_indep_instr !8, !argument_dep_instr !9, !input_dep_block !10, !control_dep_instr !11
  br label %43, !data_indep_instr !8, !argument_dep_instr !9, !control_dep_instr !11

43:                                               ; preds = %42, %41
  %44 = load i32, i32* @x, align 4
  %45 = load i32, i32* @y, align 4
  %46 = sub i32 %44, 1
  %47 = mul i32 %44, %46
  %48 = urem i32 %47, 2
  %49 = icmp eq i32 %48, 0
  %50 = icmp slt i32 %45, 10
  %51 = or i1 %49, %50
  br i1 %51, label %originalBB1, label %originalBB1alteredBB

originalBB1:                                      ; preds = %43, %originalBB1alteredBB
  store i32 0, i32* %3, align 4, !data_indep_instr !8, !argument_dep_instr !9, !input_dep_block !10, !control_dep_instr !11
  %52 = load i32, i32* @x, align 4
  %53 = load i32, i32* @y, align 4
  %54 = sub i32 %52, 1
  %55 = mul i32 %52, %54
  %56 = urem i32 %55, 2
  %57 = icmp eq i32 %56, 0
  %58 = icmp slt i32 %53, 10
  %59 = or i1 %57, %58
  br i1 %59, label %originalBBpart24, label %originalBB1alteredBB

originalBBpart24:                                 ; preds = %originalBB1
  br label %60, !data_indep_instr !8, !argument_dep_instr !9, !control_dep_instr !11

60:                                               ; preds = %originalBBpart24, %12
  %61 = load i32, i32* %3, align 4, !input_indep_block !4, !input_indep_instr !7, !data_indep_instr !8
  ret i32 %61, !input_indep_instr !7, !data_indep_instr !8

originalBBalteredBB:                              ; preds = %originalBB, %13
  %62 = load i8**, i8*** %5, align 8, !data_dep_instr !6, !argument_dep_instr !9, !input_dep_block !10, !control_dep_instr !11
  %63 = getelementptr inbounds i8*, i8** %62, i64 1, !data_dep_instr !6, !argument_dep_instr !9, !control_dep_instr !11
  %64 = load i8*, i8** %63, align 8, !data_dep_instr !6, !argument_dep_instr !9, !control_dep_instr !11
  store i8* %64, i8** %6, align 8, !data_dep_instr !6, !argument_dep_instr !9, !control_dep_instr !11
  %65 = load i8**, i8*** %5, align 8, !data_dep_instr !6, !argument_dep_instr !9, !control_dep_instr !11
  %66 = getelementptr inbounds i8*, i8** %65, i64 2, !data_dep_instr !6, !argument_dep_instr !9, !control_dep_instr !11
  %67 = load i8*, i8** %66, align 8, !data_dep_instr !6, !argument_dep_instr !9, !control_dep_instr !11
  store i8* %67, i8** %7, align 8, !data_dep_instr !6, !argument_dep_instr !9, !control_dep_instr !11
  %68 = load i8*, i8** %6, align 8, !data_dep_instr !6, !argument_dep_instr !9, !control_dep_instr !11
  %69 = load i8*, i8** %7, align 8, !data_dep_instr !6, !argument_dep_instr !9, !control_dep_instr !11
  %70 = call i32 @check_anagram(i8* %68, i8* %69), !data_indep_instr !8, !argument_dep_instr !9, !control_dep_instr !11
  store i32 %70, i32* %8, align 4, !data_indep_instr !8, !argument_dep_instr !9, !control_dep_instr !11
  %71 = load i32, i32* %8, align 4, !data_indep_instr !8, !argument_dep_instr !9, !control_dep_instr !11
  %72 = icmp eq i32 %71, 1, !data_indep_instr !8, !argument_dep_instr !9, !control_dep_instr !11
  br label %originalBB

originalBB1alteredBB:                             ; preds = %originalBB1, %43
  store i32 0, i32* %3, align 4, !data_indep_instr !8, !argument_dep_instr !9, !input_dep_block !10, !control_dep_instr !11
  br label %originalBB1
}

; Function Attrs: noinline nounwind optnone uwtable
define i32 @check_anagram(i8* %0, i8* %1) #0 !input_dep_function !12 {
  %3 = load i32, i32* @x.1, align 4
  %4 = load i32, i32* @y.2, align 4
  %5 = sub i32 %3, 1
  %6 = mul i32 %3, %5
  %7 = urem i32 %6, 2
  %8 = icmp eq i32 %7, 0
  %9 = icmp slt i32 %4, 10
  %10 = or i1 %8, %9
  br i1 %10, label %originalBB, label %originalBBalteredBB

originalBB:                                       ; preds = %2, %originalBBalteredBB
  %11 = alloca i32, align 4, !input_indep_block !4, !input_dep_instr !5, !data_dep_instr !6, !control_dep_instr !11
  %12 = alloca i8*, align 8, !input_dep_instr !5, !data_dep_instr !6, !control_dep_instr !11
  %13 = alloca i8*, align 8, !input_dep_instr !5, !data_dep_instr !6, !control_dep_instr !11
  %14 = alloca [26 x i32], align 16, !input_dep_instr !5, !data_dep_instr !6, !control_dep_instr !11
  %15 = alloca [26 x i32], align 16, !input_dep_instr !5, !data_dep_instr !6, !control_dep_instr !11
  %16 = alloca i32, align 4, !input_dep_instr !5, !data_dep_instr !6, !control_dep_instr !11
  store i8* %0, i8** %12, align 8, !input_dep_instr !5, !data_dep_instr !6, !argument_dep_instr !9, !control_dep_instr !11
  store i8* %1, i8** %13, align 8, !input_dep_instr !5, !data_dep_instr !6, !argument_dep_instr !9, !control_dep_instr !11
  %17 = bitcast [26 x i32]* %14 to i8*, !input_dep_instr !5, !data_dep_instr !6, !control_dep_instr !11
  call void @llvm.memset.p0i8.i64(i8* align 16 %17, i8 0, i64 104, i1 false), !input_indep_instr !7, !data_indep_instr !8, !control_dep_instr !11
  %18 = bitcast [26 x i32]* %15 to i8*, !input_dep_instr !5, !data_dep_instr !6, !control_dep_instr !11
  call void @llvm.memset.p0i8.i64(i8* align 16 %18, i8 0, i64 104, i1 false), !input_indep_instr !7, !data_indep_instr !8, !control_dep_instr !11
  store i32 0, i32* %16, align 4, !input_indep_instr !7, !data_indep_instr !8, !control_dep_instr !11
  %19 = load i32, i32* @x.1, align 4
  %20 = load i32, i32* @y.2, align 4
  %21 = sub i32 %19, 1
  %22 = mul i32 %19, %21
  %23 = urem i32 %22, 2
  %24 = icmp eq i32 %23, 0
  %25 = icmp slt i32 %20, 10
  %26 = or i1 %24, %25
  br i1 %26, label %originalBBpart2, label %originalBBalteredBB

originalBBpart2:                                  ; preds = %originalBB
  br label %27, !input_indep_instr !7, !data_indep_instr !8, !control_dep_instr !11

27:                                               ; preds = %originalBBpart226, %originalBBpart2
  %28 = load i8*, i8** %12, align 8, !data_dep_instr !6, !argument_dep_instr !9, !input_dep_block !10, !control_dep_instr !11
  %29 = load i32, i32* %16, align 4, !data_dep_instr !6, !argument_dep_instr !9, !control_dep_instr !11
  %30 = sext i32 %29 to i64, !data_dep_instr !6, !argument_dep_instr !9, !control_dep_instr !11
  %31 = getelementptr inbounds i8, i8* %28, i64 %30, !data_dep_instr !6, !argument_dep_instr !9, !control_dep_instr !11
  %32 = load i8, i8* %31, align 1, !data_dep_instr !6, !argument_dep_instr !9, !control_dep_instr !11
  %33 = sext i8 %32 to i32, !data_dep_instr !6, !argument_dep_instr !9, !control_dep_instr !11
  %34 = icmp ne i32 %33, 0, !data_dep_instr !6, !argument_dep_instr !9, !control_dep_instr !11
  br i1 %34, label %35, label %65, !data_dep_instr !6, !argument_dep_instr !9, !control_dep_instr !11

35:                                               ; preds = %27
  %36 = load i32, i32* @x.1, align 4
  %37 = load i32, i32* @y.2, align 4
  %38 = sub i32 %36, 1
  %39 = mul i32 %36, %38
  %40 = urem i32 %39, 2
  %41 = icmp eq i32 %40, 0
  %42 = icmp slt i32 %37, 10
  %43 = or i1 %41, %42
  br i1 %43, label %originalBB1, label %originalBB1alteredBB

originalBB1:                                      ; preds = %35, %originalBB1alteredBB
  %44 = load i8*, i8** %12, align 8, !data_dep_instr !6, !argument_dep_instr !9, !input_dep_block !10, !control_dep_instr !11
  %45 = load i32, i32* %16, align 4, !data_dep_instr !6, !argument_dep_instr !9, !control_dep_instr !11
  %46 = sext i32 %45 to i64, !data_dep_instr !6, !argument_dep_instr !9, !control_dep_instr !11
  %47 = getelementptr inbounds i8, i8* %44, i64 %46, !data_dep_instr !6, !argument_dep_instr !9, !control_dep_instr !11
  %48 = load i8, i8* %47, align 1, !data_dep_instr !6, !argument_dep_instr !9, !control_dep_instr !11
  %49 = sext i8 %48 to i32, !data_dep_instr !6, !argument_dep_instr !9, !control_dep_instr !11
  %50 = sub nsw i32 %49, 97, !data_dep_instr !6, !argument_dep_instr !9, !control_dep_instr !11
  %51 = sext i32 %50 to i64, !data_dep_instr !6, !argument_dep_instr !9, !control_dep_instr !11
  %52 = getelementptr inbounds [26 x i32], [26 x i32]* %14, i64 0, i64 %51, !data_dep_instr !6, !argument_dep_instr !9, !control_dep_instr !11
  %53 = load i32, i32* %52, align 4, !data_dep_instr !6, !argument_dep_instr !9, !control_dep_instr !11
  %54 = add nsw i32 %53, 1, !data_dep_instr !6, !argument_dep_instr !9, !control_dep_instr !11
  store i32 %54, i32* %52, align 4, !data_dep_instr !6, !argument_dep_instr !9, !control_dep_instr !11
  %55 = load i32, i32* %16, align 4, !data_dep_instr !6, !argument_dep_instr !9, !control_dep_instr !11
  %56 = add nsw i32 %55, 1, !data_dep_instr !6, !argument_dep_instr !9, !control_dep_instr !11
  store i32 %56, i32* %16, align 4, !data_dep_instr !6, !argument_dep_instr !9, !control_dep_instr !11
  %57 = load i32, i32* @x.1, align 4
  %58 = load i32, i32* @y.2, align 4
  %59 = sub i32 %57, 1
  %60 = mul i32 %57, %59
  %61 = urem i32 %60, 2
  %62 = icmp eq i32 %61, 0
  %63 = icmp slt i32 %58, 10
  %64 = or i1 %62, %63
  br i1 %64, label %originalBBpart226, label %originalBB1alteredBB

originalBBpart226:                                ; preds = %originalBB1
  br label %27, !data_indep_instr !8, !argument_dep_instr !9, !control_dep_instr !11

65:                                               ; preds = %27
  store i32 0, i32* %16, align 4, !input_indep_block !4, !input_indep_instr !7, !data_indep_instr !8, !control_dep_instr !11
  br label %66, !input_indep_instr !7, !data_indep_instr !8, !control_dep_instr !11

66:                                               ; preds = %originalBBpart242, %65
  %67 = load i8*, i8** %13, align 8, !data_dep_instr !6, !argument_dep_instr !9, !input_dep_block !10, !control_dep_instr !11
  %68 = load i32, i32* %16, align 4, !data_dep_instr !6, !argument_dep_instr !9, !control_dep_instr !11
  %69 = sext i32 %68 to i64, !data_dep_instr !6, !argument_dep_instr !9, !control_dep_instr !11
  %70 = getelementptr inbounds i8, i8* %67, i64 %69, !data_dep_instr !6, !argument_dep_instr !9, !control_dep_instr !11
  %71 = load i8, i8* %70, align 1, !data_dep_instr !6, !argument_dep_instr !9, !control_dep_instr !11
  %72 = sext i8 %71 to i32, !data_dep_instr !6, !argument_dep_instr !9, !control_dep_instr !11
  %73 = icmp ne i32 %72, 0, !data_dep_instr !6, !argument_dep_instr !9, !control_dep_instr !11
  br i1 %73, label %74, label %104, !data_dep_instr !6, !argument_dep_instr !9, !control_dep_instr !11

74:                                               ; preds = %66
  %75 = load i32, i32* @x.1, align 4
  %76 = load i32, i32* @y.2, align 4
  %77 = sub i32 %75, 1
  %78 = mul i32 %75, %77
  %79 = urem i32 %78, 2
  %80 = icmp eq i32 %79, 0
  %81 = icmp slt i32 %76, 10
  %82 = or i1 %80, %81
  br i1 %82, label %originalBB28, label %originalBB28alteredBB

originalBB28:                                     ; preds = %74, %originalBB28alteredBB
  %83 = load i8*, i8** %13, align 8, !data_dep_instr !6, !argument_dep_instr !9, !input_dep_block !10, !control_dep_instr !11
  %84 = load i32, i32* %16, align 4, !data_dep_instr !6, !argument_dep_instr !9, !control_dep_instr !11
  %85 = sext i32 %84 to i64, !data_dep_instr !6, !argument_dep_instr !9, !control_dep_instr !11
  %86 = getelementptr inbounds i8, i8* %83, i64 %85, !data_dep_instr !6, !argument_dep_instr !9, !control_dep_instr !11
  %87 = load i8, i8* %86, align 1, !data_dep_instr !6, !argument_dep_instr !9, !control_dep_instr !11
  %88 = sext i8 %87 to i32, !data_dep_instr !6, !argument_dep_instr !9, !control_dep_instr !11
  %89 = sub nsw i32 %88, 97, !data_dep_instr !6, !argument_dep_instr !9, !control_dep_instr !11
  %90 = sext i32 %89 to i64, !data_dep_instr !6, !argument_dep_instr !9, !control_dep_instr !11
  %91 = getelementptr inbounds [26 x i32], [26 x i32]* %15, i64 0, i64 %90, !data_dep_instr !6, !argument_dep_instr !9, !control_dep_instr !11
  %92 = load i32, i32* %91, align 4, !data_dep_instr !6, !argument_dep_instr !9, !control_dep_instr !11
  %93 = add nsw i32 %92, 1, !data_dep_instr !6, !argument_dep_instr !9, !control_dep_instr !11
  store i32 %93, i32* %91, align 4, !data_dep_instr !6, !argument_dep_instr !9, !control_dep_instr !11
  %94 = load i32, i32* %16, align 4, !data_dep_instr !6, !argument_dep_instr !9, !control_dep_instr !11
  %95 = add nsw i32 %94, 1, !data_dep_instr !6, !argument_dep_instr !9, !control_dep_instr !11
  store i32 %95, i32* %16, align 4, !data_dep_instr !6, !argument_dep_instr !9, !control_dep_instr !11
  %96 = load i32, i32* @x.1, align 4
  %97 = load i32, i32* @y.2, align 4
  %98 = sub i32 %96, 1
  %99 = mul i32 %96, %98
  %100 = urem i32 %99, 2
  %101 = icmp eq i32 %100, 0
  %102 = icmp slt i32 %97, 10
  %103 = or i1 %101, %102
  br i1 %103, label %originalBBpart242, label %originalBB28alteredBB

originalBBpart242:                                ; preds = %originalBB28
  br label %66, !data_indep_instr !8, !argument_dep_instr !9, !control_dep_instr !11

104:                                              ; preds = %66
  store i32 0, i32* %16, align 4, !input_indep_block !4, !input_indep_instr !7, !data_indep_instr !8, !control_dep_instr !11
  br label %105, !input_indep_instr !7, !data_indep_instr !8, !control_dep_instr !11

105:                                              ; preds = %136, %104
  %106 = load i32, i32* @x.1, align 4
  %107 = load i32, i32* @y.2, align 4
  %108 = sub i32 %106, 1
  %109 = mul i32 %106, %108
  %110 = urem i32 %109, 2
  %111 = icmp eq i32 %110, 0
  %112 = icmp slt i32 %107, 10
  %113 = or i1 %111, %112
  br i1 %113, label %originalBB44, label %originalBB44alteredBB

originalBB44:                                     ; preds = %105, %originalBB44alteredBB
  %114 = load i32, i32* %16, align 4, !data_dep_instr !6, !argument_dep_instr !9, !input_dep_block !10, !control_dep_instr !11
  %115 = icmp slt i32 %114, 26, !data_dep_instr !6, !argument_dep_instr !9, !control_dep_instr !11
  %116 = load i32, i32* @x.1, align 4
  %117 = load i32, i32* @y.2, align 4
  %118 = sub i32 %116, 1
  %119 = mul i32 %116, %118
  %120 = urem i32 %119, 2
  %121 = icmp eq i32 %120, 0
  %122 = icmp slt i32 %117, 10
  %123 = or i1 %121, %122
  br i1 %123, label %originalBBpart246, label %originalBB44alteredBB

originalBBpart246:                                ; preds = %originalBB44
  br i1 %115, label %124, label %137, !data_dep_instr !6, !argument_dep_instr !9, !control_dep_instr !11

124:                                              ; preds = %originalBBpart246
  %125 = load i32, i32* %16, align 4, !data_dep_instr !6, !argument_dep_instr !9, !input_dep_block !10, !control_dep_instr !11
  %126 = sext i32 %125 to i64, !data_dep_instr !6, !argument_dep_instr !9, !control_dep_instr !11
  %127 = getelementptr inbounds [26 x i32], [26 x i32]* %14, i64 0, i64 %126, !data_dep_instr !6, !argument_dep_instr !9, !control_dep_instr !11
  %128 = load i32, i32* %127, align 4, !data_dep_instr !6, !argument_dep_instr !9, !control_dep_instr !11
  %129 = load i32, i32* %16, align 4, !data_dep_instr !6, !argument_dep_instr !9, !control_dep_instr !11
  %130 = sext i32 %129 to i64, !data_dep_instr !6, !argument_dep_instr !9, !control_dep_instr !11
  %131 = getelementptr inbounds [26 x i32], [26 x i32]* %15, i64 0, i64 %130, !data_dep_instr !6, !argument_dep_instr !9, !control_dep_instr !11
  %132 = load i32, i32* %131, align 4, !data_dep_instr !6, !argument_dep_instr !9, !control_dep_instr !11
  %133 = icmp ne i32 %128, %132, !data_dep_instr !6, !argument_dep_instr !9, !control_dep_instr !11
  br i1 %133, label %134, label %135, !data_dep_instr !6, !argument_dep_instr !9, !control_dep_instr !11

134:                                              ; preds = %124
  store i32 0, i32* %11, align 4, !data_indep_instr !8, !argument_dep_instr !9, !input_dep_block !10, !control_dep_instr !11
  br label %154, !data_indep_instr !8, !argument_dep_instr !9, !control_dep_instr !11

135:                                              ; preds = %124
  br label %136, !data_indep_instr !8, !argument_dep_instr !9, !input_dep_block !10, !control_dep_instr !11

136:                                              ; preds = %135
  call void @check_anagram0(i32* %16), !data_indep_instr !8, !argument_dep_instr !9, !input_dep_block !10, !control_dep_instr !11
  br label %105, !data_indep_instr !8, !argument_dep_instr !9, !control_dep_instr !11

137:                                              ; preds = %originalBBpart246
  %138 = load i32, i32* @x.1, align 4
  %139 = load i32, i32* @y.2, align 4
  %140 = sub i32 %138, 1
  %141 = mul i32 %138, %140
  %142 = urem i32 %141, 2
  %143 = icmp eq i32 %142, 0
  %144 = icmp slt i32 %139, 10
  %145 = or i1 %143, %144
  br i1 %145, label %originalBB48, label %originalBB48alteredBB

originalBB48:                                     ; preds = %137, %originalBB48alteredBB
  store i32 1, i32* %11, align 4, !data_indep_instr !8, !argument_dep_instr !9, !input_dep_block !10, !control_dep_instr !11
  %146 = load i32, i32* @x.1, align 4
  %147 = load i32, i32* @y.2, align 4
  %148 = sub i32 %146, 1
  %149 = mul i32 %146, %148
  %150 = urem i32 %149, 2
  %151 = icmp eq i32 %150, 0
  %152 = icmp slt i32 %147, 10
  %153 = or i1 %151, %152
  br i1 %153, label %originalBBpart250, label %originalBB48alteredBB

originalBBpart250:                                ; preds = %originalBB48
  br label %154, !data_indep_instr !8, !argument_dep_instr !9, !control_dep_instr !11

154:                                              ; preds = %originalBBpart250, %134
  %155 = load i32, i32* @x.1, align 4
  %156 = load i32, i32* @y.2, align 4
  %157 = sub i32 %155, 1
  %158 = mul i32 %155, %157
  %159 = urem i32 %158, 2
  %160 = icmp eq i32 %159, 0
  %161 = icmp slt i32 %156, 10
  %162 = or i1 %160, %161
  br i1 %162, label %originalBB52, label %originalBB52alteredBB

originalBB52:                                     ; preds = %154, %originalBB52alteredBB
  %163 = load i32, i32* %11, align 4, !input_indep_block !4, !input_indep_instr !7, !data_indep_instr !8, !control_dep_instr !11
  %164 = load i32, i32* @x.1, align 4
  %165 = load i32, i32* @y.2, align 4
  %166 = sub i32 %164, 1
  %167 = mul i32 %164, %166
  %168 = urem i32 %167, 2
  %169 = icmp eq i32 %168, 0
  %170 = icmp slt i32 %165, 10
  %171 = or i1 %169, %170
  br i1 %171, label %originalBBpart254, label %originalBB52alteredBB

originalBBpart254:                                ; preds = %originalBB52
  ret i32 %163, !input_indep_instr !7, !data_indep_instr !8, !control_dep_instr !11

originalBBalteredBB:                              ; preds = %originalBB, %2
  %172 = alloca i32, align 4
  %173 = alloca i8*, align 8
  %174 = alloca i8*, align 8
  %175 = alloca [26 x i32], align 16
  %176 = alloca [26 x i32], align 16
  %177 = alloca i32, align 4
  store i8* %0, i8** %173, align 8
  store i8* %1, i8** %174, align 8
  %178 = bitcast [26 x i32]* %175 to i8*
  call void @llvm.memset.p0i8.i64(i8* align 16 %178, i8 0, i64 104, i1 false)
  %179 = bitcast [26 x i32]* %176 to i8*
  call void @llvm.memset.p0i8.i64(i8* align 16 %179, i8 0, i64 104, i1 false)
  store i32 0, i32* %177, align 4
  br label %originalBB

originalBB1alteredBB:                             ; preds = %originalBB1, %35
  %180 = load i8*, i8** %12, align 8, !data_dep_instr !6, !argument_dep_instr !9, !input_dep_block !10, !control_dep_instr !11
  %181 = load i32, i32* %16, align 4, !data_dep_instr !6, !argument_dep_instr !9, !control_dep_instr !11
  %182 = sext i32 %181 to i64, !data_dep_instr !6, !argument_dep_instr !9, !control_dep_instr !11
  %183 = getelementptr inbounds i8, i8* %180, i64 %182, !data_dep_instr !6, !argument_dep_instr !9, !control_dep_instr !11
  %184 = load i8, i8* %183, align 1, !data_dep_instr !6, !argument_dep_instr !9, !control_dep_instr !11
  %185 = sext i8 %184 to i32, !data_dep_instr !6, !argument_dep_instr !9, !control_dep_instr !11
  %_ = sub i32 %185, 97
  %gen = mul i32 %_, 97
  %_2 = sub i32 %185, 97
  %gen3 = mul i32 %_2, 97
  %_4 = sub i32 0, %185
  %gen5 = add i32 %_4, 97
  %_6 = shl i32 %185, 97
  %_7 = sub i32 0, %185
  %gen8 = add i32 %_7, 97
  %186 = sub nsw i32 %185, 97, !data_dep_instr !6, !argument_dep_instr !9, !control_dep_instr !11
  %187 = sext i32 %186 to i64, !data_dep_instr !6, !argument_dep_instr !9, !control_dep_instr !11
  %188 = getelementptr inbounds [26 x i32], [26 x i32]* %14, i64 0, i64 %187, !data_dep_instr !6, !argument_dep_instr !9, !control_dep_instr !11
  %189 = load i32, i32* %188, align 4, !data_dep_instr !6, !argument_dep_instr !9, !control_dep_instr !11
  %_9 = sub i32 %189, 1
  %gen10 = mul i32 %_9, 1
  %_11 = sub i32 0, %189
  %gen12 = add i32 %_11, 1
  %_13 = sub i32 %189, 1
  %gen14 = mul i32 %_13, 1
  %_15 = shl i32 %189, 1
  %190 = add nsw i32 %189, 1, !data_dep_instr !6, !argument_dep_instr !9, !control_dep_instr !11
  store i32 %190, i32* %188, align 4, !data_dep_instr !6, !argument_dep_instr !9, !control_dep_instr !11
  %191 = load i32, i32* %16, align 4, !data_dep_instr !6, !argument_dep_instr !9, !control_dep_instr !11
  %_16 = shl i32 %191, 1
  %_17 = shl i32 %191, 1
  %_18 = sub i32 0, %191
  %gen19 = add i32 %_18, 1
  %_20 = sub i32 0, %191
  %gen21 = add i32 %_20, 1
  %_22 = shl i32 %191, 1
  %_23 = sub i32 %191, 1
  %gen24 = mul i32 %_23, 1
  %192 = add nsw i32 %191, 1, !data_dep_instr !6, !argument_dep_instr !9, !control_dep_instr !11
  store i32 %192, i32* %16, align 4, !data_dep_instr !6, !argument_dep_instr !9, !control_dep_instr !11
  br label %originalBB1

originalBB28alteredBB:                            ; preds = %originalBB28, %74
  %193 = load i8*, i8** %13, align 8, !data_dep_instr !6, !argument_dep_instr !9, !input_dep_block !10, !control_dep_instr !11
  %194 = load i32, i32* %16, align 4, !data_dep_instr !6, !argument_dep_instr !9, !control_dep_instr !11
  %195 = sext i32 %194 to i64, !data_dep_instr !6, !argument_dep_instr !9, !control_dep_instr !11
  %196 = getelementptr inbounds i8, i8* %193, i64 %195, !data_dep_instr !6, !argument_dep_instr !9, !control_dep_instr !11
  %197 = load i8, i8* %196, align 1, !data_dep_instr !6, !argument_dep_instr !9, !control_dep_instr !11
  %198 = sext i8 %197 to i32, !data_dep_instr !6, !argument_dep_instr !9, !control_dep_instr !11
  %_29 = sub i32 0, %198
  %gen30 = add i32 %_29, 97
  %_31 = shl i32 %198, 97
  %_32 = sub i32 0, %198
  %gen33 = add i32 %_32, 97
  %199 = sub nsw i32 %198, 97, !data_dep_instr !6, !argument_dep_instr !9, !control_dep_instr !11
  %200 = sext i32 %199 to i64, !data_dep_instr !6, !argument_dep_instr !9, !control_dep_instr !11
  %201 = getelementptr inbounds [26 x i32], [26 x i32]* %15, i64 0, i64 %200, !data_dep_instr !6, !argument_dep_instr !9, !control_dep_instr !11
  %202 = load i32, i32* %201, align 4, !data_dep_instr !6, !argument_dep_instr !9, !control_dep_instr !11
  %203 = add nsw i32 %202, 1, !data_dep_instr !6, !argument_dep_instr !9, !control_dep_instr !11
  store i32 %203, i32* %201, align 4, !data_dep_instr !6, !argument_dep_instr !9, !control_dep_instr !11
  %204 = load i32, i32* %16, align 4, !data_dep_instr !6, !argument_dep_instr !9, !control_dep_instr !11
  %_34 = sub i32 %204, 1
  %gen35 = mul i32 %_34, 1
  %_36 = sub i32 0, %204
  %gen37 = add i32 %_36, 1
  %_38 = sub i32 0, %204
  %gen39 = add i32 %_38, 1
  %_40 = shl i32 %204, 1
  %205 = add nsw i32 %204, 1, !data_dep_instr !6, !argument_dep_instr !9, !control_dep_instr !11
  store i32 %205, i32* %16, align 4, !data_dep_instr !6, !argument_dep_instr !9, !control_dep_instr !11
  br label %originalBB28

originalBB44alteredBB:                            ; preds = %originalBB44, %105
  %206 = load i32, i32* %16, align 4, !data_dep_instr !6, !argument_dep_instr !9, !input_dep_block !10, !control_dep_instr !11
  %207 = icmp slt i32 %206, 26, !data_dep_instr !6, !argument_dep_instr !9, !control_dep_instr !11
  br label %originalBB44

originalBB48alteredBB:                            ; preds = %originalBB48, %137
  store i32 1, i32* %11, align 4, !data_indep_instr !8, !argument_dep_instr !9, !input_dep_block !10, !control_dep_instr !11
  br label %originalBB48

originalBB52alteredBB:                            ; preds = %originalBB52, %154
  %208 = load i32, i32* %11, align 4, !input_indep_block !4, !input_indep_instr !7, !data_indep_instr !8, !control_dep_instr !11
  br label %originalBB52
}

declare i32 @printf(i8*, ...) #1

; Function Attrs: argmemonly nofree nosync nounwind willreturn writeonly
declare void @llvm.memset.p0i8.i64(i8* nocapture writeonly, i8, i64, i1 immarg) #2

define void @main0(i8** %0, i8** %1) #3 !extracted !13 !input_dep_function !12 {
entry:
  %.ptr = alloca i8**, align 8, !input_indep_block !4, !input_dep_instr !5, !data_dep_instr !6, !control_dep_instr !11
  store i8** %0, i8*** %.ptr, align 8, !input_dep_instr !5, !data_dep_instr !6, !argument_dep_instr !9, !control_dep_instr !11
  %.el = alloca i8*, align 8, !input_dep_instr !5, !data_dep_instr !6, !control_dep_instr !11
  %2 = load i8**, i8*** %.ptr, align 8, !input_dep_instr !5, !data_dep_instr !6, !argument_dep_instr !9, !control_dep_instr !11
  %3 = load i8*, i8** %2, align 8, !input_dep_instr !5, !data_dep_instr !6, !argument_dep_instr !9, !control_dep_instr !11
  store i8* %3, i8** %.el, align 8, !input_dep_instr !5, !data_dep_instr !6, !argument_dep_instr !9, !control_dep_instr !11
  %.ptr1 = alloca i8**, align 8, !input_dep_instr !5, !data_dep_instr !6, !control_dep_instr !11
  store i8** %1, i8*** %.ptr1, align 8, !input_dep_instr !5, !data_dep_instr !6, !argument_dep_instr !9, !control_dep_instr !11
  %.el2 = alloca i8*, align 8, !input_dep_instr !5, !data_dep_instr !6, !control_dep_instr !11
  %4 = load i8**, i8*** %.ptr1, align 8, !input_dep_instr !5, !data_dep_instr !6, !argument_dep_instr !9, !control_dep_instr !11
  %5 = load i8*, i8** %4, align 8, !input_dep_instr !5, !data_dep_instr !6, !argument_dep_instr !9, !control_dep_instr !11
  store i8* %5, i8** %.el2, align 8, !input_dep_instr !5, !data_dep_instr !6, !argument_dep_instr !9, !control_dep_instr !11
  %6 = load i8*, i8** %.el2, align 8, !input_dep_instr !5, !data_dep_instr !6, !argument_dep_instr !9, !control_dep_instr !11
  %7 = load i8*, i8** %.el, align 8, !input_dep_instr !5, !data_dep_instr !6, !argument_dep_instr !9, !control_dep_instr !11
  %8 = call i32 (i8*, ...) @printf(i8* getelementptr inbounds ([29 x i8], [29 x i8]* @.str, i32 0, i32 0), i8* %6, i8* %7), !input_dep_instr !5, !data_dep_instr !6, !control_dep_instr !11
  %9 = load i8**, i8*** %.ptr1, align 8, !input_dep_instr !5, !data_dep_instr !6, !argument_dep_instr !9, !control_dep_instr !11
  %10 = load i8*, i8** %.el2, align 8, !input_dep_instr !5, !data_dep_instr !6, !argument_dep_instr !9, !control_dep_instr !11
  store i8* %10, i8** %9, align 8, !extraction_store !14, !input_dep_instr !5, !data_dep_instr !6, !argument_dep_instr !9, !control_dep_instr !11
  %11 = load i8**, i8*** %.ptr, align 8, !input_dep_instr !5, !data_dep_instr !6, !argument_dep_instr !9, !control_dep_instr !11
  %12 = load i8*, i8** %.el, align 8, !input_dep_instr !5, !data_dep_instr !6, !argument_dep_instr !9, !control_dep_instr !11
  store i8* %12, i8** %11, align 8, !extraction_store !15, !input_dep_instr !5, !data_dep_instr !6, !argument_dep_instr !9, !control_dep_instr !11
  ret void, !input_indep_instr !7, !data_indep_instr !8, !control_dep_instr !11
}

define void @main1(i8** %0, i8** %1) #3 !extracted !13 !input_dep_function !12 {
entry:
  %2 = load i32, i32* @x.5, align 4
  %3 = load i32, i32* @y.6, align 4
  %4 = sub i32 %2, 1
  %5 = mul i32 %2, %4
  %6 = urem i32 %5, 2
  %7 = icmp eq i32 %6, 0
  %8 = icmp slt i32 %3, 10
  %9 = or i1 %7, %8
  br i1 %9, label %originalBB, label %originalBBalteredBB

originalBB:                                       ; preds = %entry, %originalBBalteredBB
  %.ptr = alloca i8**, align 8, !input_indep_block !4, !input_dep_instr !5, !data_dep_instr !6, !control_dep_instr !11
  store i8** %0, i8*** %.ptr, align 8, !input_dep_instr !5, !data_dep_instr !6, !argument_dep_instr !9, !control_dep_instr !11
  %.el = alloca i8*, align 8, !input_dep_instr !5, !data_dep_instr !6, !control_dep_instr !11
  %10 = load i8**, i8*** %.ptr, align 8, !input_dep_instr !5, !data_dep_instr !6, !argument_dep_instr !9, !control_dep_instr !11
  %11 = load i8*, i8** %10, align 8, !input_dep_instr !5, !data_dep_instr !6, !argument_dep_instr !9, !control_dep_instr !11
  store i8* %11, i8** %.el, align 8, !input_dep_instr !5, !data_dep_instr !6, !argument_dep_instr !9, !control_dep_instr !11
  %.ptr1 = alloca i8**, align 8, !input_dep_instr !5, !data_dep_instr !6, !control_dep_instr !11
  store i8** %1, i8*** %.ptr1, align 8, !input_dep_instr !5, !data_dep_instr !6, !argument_dep_instr !9, !control_dep_instr !11
  %.el2 = alloca i8*, align 8, !input_dep_instr !5, !data_dep_instr !6, !control_dep_instr !11
  %12 = load i8**, i8*** %.ptr1, align 8, !input_dep_instr !5, !data_dep_instr !6, !argument_dep_instr !9, !control_dep_instr !11
  %13 = load i8*, i8** %12, align 8, !input_dep_instr !5, !data_dep_instr !6, !argument_dep_instr !9, !control_dep_instr !11
  store i8* %13, i8** %.el2, align 8, !input_dep_instr !5, !data_dep_instr !6, !argument_dep_instr !9, !control_dep_instr !11
  %14 = load i8*, i8** %.el2, align 8, !input_dep_instr !5, !data_dep_instr !6, !argument_dep_instr !9, !control_dep_instr !11
  %15 = load i8*, i8** %.el, align 8, !input_dep_instr !5, !data_dep_instr !6, !argument_dep_instr !9, !control_dep_instr !11
  %16 = call i32 (i8*, ...) @printf(i8* getelementptr inbounds ([33 x i8], [33 x i8]* @.str.1, i32 0, i32 0), i8* %14, i8* %15), !input_dep_instr !5, !data_dep_instr !6, !control_dep_instr !11
  %17 = load i8**, i8*** %.ptr1, align 8, !input_dep_instr !5, !data_dep_instr !6, !argument_dep_instr !9, !control_dep_instr !11
  %18 = load i8*, i8** %.el2, align 8, !input_dep_instr !5, !data_dep_instr !6, !argument_dep_instr !9, !control_dep_instr !11
  store i8* %18, i8** %17, align 8, !extraction_store !14, !input_dep_instr !5, !data_dep_instr !6, !argument_dep_instr !9, !control_dep_instr !11
  %19 = load i8**, i8*** %.ptr, align 8, !input_dep_instr !5, !data_dep_instr !6, !argument_dep_instr !9, !control_dep_instr !11
  %20 = load i8*, i8** %.el, align 8, !input_dep_instr !5, !data_dep_instr !6, !argument_dep_instr !9, !control_dep_instr !11
  store i8* %20, i8** %19, align 8, !extraction_store !15, !input_dep_instr !5, !data_dep_instr !6, !argument_dep_instr !9, !control_dep_instr !11
  %21 = load i32, i32* @x.5, align 4
  %22 = load i32, i32* @y.6, align 4
  %23 = sub i32 %21, 1
  %24 = mul i32 %21, %23
  %25 = urem i32 %24, 2
  %26 = icmp eq i32 %25, 0
  %27 = icmp slt i32 %22, 10
  %28 = or i1 %26, %27
  br i1 %28, label %originalBBpart2, label %originalBBalteredBB

originalBBpart2:                                  ; preds = %originalBB
  ret void, !input_indep_instr !7, !data_indep_instr !8, !control_dep_instr !11

originalBBalteredBB:                              ; preds = %originalBB, %entry
  %.ptralteredBB = alloca i8**, align 8, !input_indep_block !4, !input_dep_instr !5, !data_dep_instr !6, !control_dep_instr !11
  store i8** %0, i8*** %.ptralteredBB, align 8, !input_dep_instr !5, !data_dep_instr !6, !argument_dep_instr !9, !control_dep_instr !11
  %.elalteredBB = alloca i8*, align 8, !input_dep_instr !5, !data_dep_instr !6, !control_dep_instr !11
  %29 = load i8**, i8*** %.ptralteredBB, align 8, !input_dep_instr !5, !data_dep_instr !6, !argument_dep_instr !9, !control_dep_instr !11
  %30 = load i8*, i8** %29, align 8, !input_dep_instr !5, !data_dep_instr !6, !argument_dep_instr !9, !control_dep_instr !11
  store i8* %30, i8** %.elalteredBB, align 8, !input_dep_instr !5, !data_dep_instr !6, !argument_dep_instr !9, !control_dep_instr !11
  %.ptr1alteredBB = alloca i8**, align 8, !input_dep_instr !5, !data_dep_instr !6, !control_dep_instr !11
  store i8** %1, i8*** %.ptr1alteredBB, align 8, !input_dep_instr !5, !data_dep_instr !6, !argument_dep_instr !9, !control_dep_instr !11
  %.el2alteredBB = alloca i8*, align 8, !input_dep_instr !5, !data_dep_instr !6, !control_dep_instr !11
  %31 = load i8**, i8*** %.ptr1alteredBB, align 8, !input_dep_instr !5, !data_dep_instr !6, !argument_dep_instr !9, !control_dep_instr !11
  %32 = load i8*, i8** %31, align 8, !input_dep_instr !5, !data_dep_instr !6, !argument_dep_instr !9, !control_dep_instr !11
  store i8* %32, i8** %.el2alteredBB, align 8, !input_dep_instr !5, !data_dep_instr !6, !argument_dep_instr !9, !control_dep_instr !11
  %33 = load i8*, i8** %.el2alteredBB, align 8, !input_dep_instr !5, !data_dep_instr !6, !argument_dep_instr !9, !control_dep_instr !11
  %34 = load i8*, i8** %.elalteredBB, align 8, !input_dep_instr !5, !data_dep_instr !6, !argument_dep_instr !9, !control_dep_instr !11
  %35 = call i32 (i8*, ...) @printf(i8* getelementptr inbounds ([33 x i8], [33 x i8]* @.str.1, i32 0, i32 0), i8* %33, i8* %34), !input_dep_instr !5, !data_dep_instr !6, !control_dep_instr !11
  %36 = load i8**, i8*** %.ptr1alteredBB, align 8, !input_dep_instr !5, !data_dep_instr !6, !argument_dep_instr !9, !control_dep_instr !11
  %37 = load i8*, i8** %.el2alteredBB, align 8, !input_dep_instr !5, !data_dep_instr !6, !argument_dep_instr !9, !control_dep_instr !11
  store i8* %37, i8** %36, align 8, !extraction_store !14, !input_dep_instr !5, !data_dep_instr !6, !argument_dep_instr !9, !control_dep_instr !11
  %38 = load i8**, i8*** %.ptralteredBB, align 8, !input_dep_instr !5, !data_dep_instr !6, !argument_dep_instr !9, !control_dep_instr !11
  %39 = load i8*, i8** %.elalteredBB, align 8, !input_dep_instr !5, !data_dep_instr !6, !argument_dep_instr !9, !control_dep_instr !11
  store i8* %39, i8** %38, align 8, !extraction_store !15, !input_dep_instr !5, !data_dep_instr !6, !argument_dep_instr !9, !control_dep_instr !11
  br label %originalBB
}

define void @check_anagram0(i32* %0) #3 !extracted !13 !input_dep_function !12 {
entry:
  %.ptr = alloca i32*, align 8, !input_indep_block !4, !input_dep_instr !5, !data_dep_instr !6, !control_dep_instr !11
  store i32* %0, i32** %.ptr, align 8, !input_indep_instr !7, !data_indep_instr !8, !argument_dep_instr !9, !control_dep_instr !11
  %.el = alloca i32, align 4, !input_dep_instr !5, !data_dep_instr !6, !control_dep_instr !11
  %1 = load i32*, i32** %.ptr, align 8, !input_indep_instr !7, !data_indep_instr !8, !argument_dep_instr !9, !control_dep_instr !11
  %2 = load i32, i32* %1, align 4, !input_indep_instr !7, !data_indep_instr !8, !argument_dep_instr !9, !control_dep_instr !11
  store i32 %2, i32* %.el, align 4, !input_indep_instr !7, !data_indep_instr !8, !argument_dep_instr !9, !control_dep_instr !11
  %3 = load i32, i32* %.el, align 4, !input_indep_instr !7, !data_indep_instr !8, !argument_dep_instr !9, !control_dep_instr !11
  %4 = add nsw i32 %3, 1, !input_indep_instr !7, !data_indep_instr !8, !argument_dep_instr !9, !control_dep_instr !11
  store i32 %4, i32* %.el, align 4, !input_indep_instr !7, !data_indep_instr !8, !argument_dep_instr !9, !control_dep_instr !11
  %5 = load i32*, i32** %.ptr, align 8, !input_indep_instr !7, !data_indep_instr !8, !argument_dep_instr !9, !control_dep_instr !11
  %6 = load i32, i32* %.el, align 4, !input_indep_instr !7, !data_indep_instr !8, !argument_dep_instr !9, !control_dep_instr !11
  store i32 %6, i32* %5, align 4, !extraction_store !15, !input_indep_instr !7, !data_indep_instr !8, !argument_dep_instr !9, !control_dep_instr !11
  ret void, !input_indep_instr !7, !data_indep_instr !8, !control_dep_instr !11
}

attributes #0 = { noinline nounwind optnone uwtable "bcf" "correctly-rounded-divide-sqrt-fp-math"="false" "disable-tail-calls"="false" "frame-pointer"="all" "less-precise-fpmad"="false" "no-infs-fp-math"="false" "no-jump-tables"="false" "no-nans-fp-math"="false" "no-signed-zeros-fp-math"="false" "no-trapping-math"="false" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+fxsr,+mmx,+sse,+sse2,+x87" "unsafe-fp-math"="false" "use-soft-float"="false" }
attributes #1 = { "bcf" "correctly-rounded-divide-sqrt-fp-math"="false" "disable-tail-calls"="false" "frame-pointer"="all" "less-precise-fpmad"="false" "no-infs-fp-math"="false" "no-nans-fp-math"="false" "no-signed-zeros-fp-math"="false" "no-trapping-math"="false" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+fxsr,+mmx,+sse,+sse2,+x87" "unsafe-fp-math"="false" "use-soft-float"="false" }
attributes #2 = { argmemonly nofree nosync nounwind willreturn writeonly }
attributes #3 = { "bcf" }

!llvm.module.flags = !{!0, !1}
!llvm.ident = !{!2}

!0 = !{i32 1, !"wchar_size", i32 4}
!1 = !{i32 1, !"cached_input_dep", i32 1}
!2 = !{!"clang version 6.0.1-svn334776-1~exp1~20180912093054.102 (branches/release_60)"}
!3 = !{!"input_indep_function"}
!4 = !{!"input_indep_block"}
!5 = !{!"input_dep_instr"}
!6 = !{!"data_dep_instr"}
!7 = !{!"input_indep_instr"}
!8 = !{!"data_indep_instr"}
!9 = !{!"argument_dep_instr"}
!10 = !{!"input_dep_block"}
!11 = !{!"control_dep_instr"}
!12 = !{!"input_dep_function"}
!13 = !{!"extracted"}
!14 = !{i32 1}
!15 = !{i32 0}
